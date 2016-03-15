#!/usr/bin/env python
"""
Segment subject for selected thalamic nuclei using whole-brain registration via a template and PICSL label fusion.
"""
import os
import sys
import argparse
import tempfile
import time
import parallel
from shutil import rmtree
from functools import partial
from collections import OrderedDict
from datetime import timedelta
from imgtools import check_warps, sanitize_input, flip_lr, label_fusion_picsl_ants, ants_compose_a_to_b, ants_apply_only_warp
from ants_nonlinear import ants_nonlinear_registration, bias_correct
from THOMAS_constants import image_name, template, this_path, prior_path, subjects, roi, roi_choices, optimal


def warp_atlas_subject(subject, path, labels, input_image, input_transform_prefix, output_path, exec_options={}):
    """
    Warp a training set subject's labels to input_image.
    """
    a_transform_prefix = os.path.join(path, subject+'/WMnMPRAGE')
    output_path = os.path.join(output_path, subject)
    try:
        os.mkdir(output_path)
    except OSError:
        # Exists
        pass
    combined_warp = os.path.join(output_path, 'Warp.nii.gz')
    ants_compose_a_to_b(a_transform_prefix, b_path=input_image, b_transform_prefix=input_transform_prefix, output=combined_warp, **exec_options)
    output_labels = {}
    # OPT parallelize, or merge parallelism with subject level
    for label in labels:
        label_fname = os.path.join(path, subject, 'sanitized_rois', label+'.nii.gz')
        warped_label = os.path.join(output_path, label+'.nii.gz')
        switches = '--use-NN'
        ants_apply_only_warp(template=input_image, input_image=label_fname, input_warp=combined_warp, output_image=warped_label, switches=switches, **exec_options)
        output_labels[label] = warped_label
    # Warp anatomical WMnMPRAGE_bias_corr too
    # TODO merge this into previous for loop to be DRY?
    output_image, _ = ants_apply_only_warp(
        template=input_image,
        input_image=os.path.join(path, subject, image_name),
        input_warp=combined_warp,
        output_image=os.path.join(output_path, image_name),
        switches='--use-BSpline',
        **exec_options
    )
    output_labels['WMnMPRAGE_bias_corr'] = output_image
    return output_labels


exec_options = {'echo': False, 'suppress': True}
parallel_command = partial(parallel.command, **exec_options)


parser = argparse.ArgumentParser(description='Thalamic segmentation of a WMnMPRAGE image using STEPS label fusion and the Tourdias atlas. [refs]  Whole-brain template registration pipeline.')
parser.add_argument('input_image', help='input WMnMPRAGE NiFTI image, may need to be in LR PA IS format')
parser.add_argument('output_path', help='the output file for single ROI or directory for multiple ROIs')
parser.add_argument('roi_names', metavar='roi_names', choices=roi_choices, nargs='+', help='a space separated list of one or more ROIs.  Valid targets are: %s' % ', '.join(roi_choices))
parser.add_argument('-w', '--warp', metavar='path', help='looks for {path}InverseWarp.nii.gz and {path}Affine.txt instead of basing it off input_image.')
parser.add_argument('-F', '--forcereg', action='store_true', help='force ANTS registration to WMnMPRAGE mean brain template. The --warp argument can be then used to specify the output path.')
parser.add_argument('-p', '--processes', nargs='?', default=None, const=None, type=int, help='number of parallel processes to use.  If unspecified, automatically set to number of CPUs.')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
parser.add_argument('-d', '--debug', action='store_true', help='debug mode, interactive prompts')
parser.add_argument('-R', '--right', action='store_true', help='segment right thalamus')
parser.add_argument('--tempdir', help='temporary directory to store registered atlases.  This will not be deleted as usual.')
# TODO handle single roi, single output file case
# TODO fix verbose and debug
# TODO go back to shell=False for command to suppress output and then fix sanitize labels


def main(args, temp_path, pool):
    input_image = orig_input_image = args.input_image
    output_path = args.output_path
    if roi['param_all'] in args.roi_names:
        labels = list(roi['label_names'])
    else:
        roi_dict = dict(zip(roi['param_names'], roi['label_names']))
        labels = [roi_dict[el] for el in args.roi_names]

    if args.warp:
        warp_path = args.warp
    else:
        # TODO remove this as the default behavior, instead do ANTS?
        head, tail = os.path.split(input_image)
        tail = tail.replace('.nii', '').replace('.gz', '') #split('.', 1)[0]
        warp_path = os.path.join(temp_path, tail)

    t = time.time()
    input_image = sanitize_input(input_image, temp_path)
    if args.right:
        flip_lr(input_image, input_image)
    print '--- Correcting bias. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    _, cmd = bias_correct(input_image, input_image, **exec_options)
    print '--- Registering to mean brain template. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    if args.forcereg or not check_warps(warp_path):
        if not args.warp:
            warp_path = os.path.join(temp_path, tail)
            print 'Saving output to temporary path.'
        else:
            print 'Saving output as %s' % warp_path
        _, _, cmd = ants_nonlinear_registration(template, input_image, warp_path, **exec_options)
    else:
        print 'Skipped, using %sInverseWarp.nii.gz and %sAffine.txt' % (warp_path, warp_path)
    print '--- Warping prior labels and images. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    # TODO should probably use output from warp_atlas_subject instead of hard coding paths in create_atlas
    # TODO make this more parallel
    warped_labels = pool.map(partial(
        warp_atlas_subject,
        path=prior_path,
        labels=labels,
        input_image=input_image,
        input_transform_prefix=warp_path,
        output_path=temp_path,
        exec_options=exec_options,
    ), subjects)
    warped_labels = {label: {subj: d[label] for subj, d in zip(subjects, warped_labels)} for label in warped_labels[0]}
    # print '--- Forming subject-registered atlases. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    # atlases = pool.map(partial(create_atlas, path=temp_path, subjects=subjects, target='', echo=exec_options['echo']),
    #     [{'label': label, 'output_atlas': os.path.join(temp_path, label+'_atlas.nii.gz')} for label in warped_labels])
    # atlases = dict(zip(warped_labels, zip(*atlases)[0]))
    print '--- Performing label fusion. --- Elapsed: %s' % timedelta(seconds=time.time()-t)
    # FIXME use whole-brain template registration optimized parameters instead, these are from crop pipeline
    atlas_images = warped_labels['WMnMPRAGE_bias_corr'].values()
    optimal_picsl = optimal['PICSL']
    # for k, v in warped_labels.iteritems():
    #     print k, v
    # for label in labels:
    #     print optimal_picsl[label]
    pool.map(partial(label_fusion_picsl_ants, input_image, atlas_images),
        [dict(
            atlas_labels=warped_labels[label].values(),
            output_label=os.path.join(temp_path, label+'.nii.gz'),
            rp=optimal_picsl[label]['rp'],
            rs=optimal_picsl[label]['rs'],
            beta=optimal_picsl[label]['beta'],
            **exec_options
        ) for label in labels])
    # # STEPS
    # pool_small.map(partial(label_fusion, input_image=input_image, image_atlas=atlases['WMnMPRAGE_bias_corr'], echo=exec_options['echo']),
    #     [{
    #         'label_atlas': atlases[label],
    #         'output_label': os.path.join(output_path, label+'.nii.gz'),
    #         'sigma': optimal_steps[label]['steps_sigma'],
    #         'X': optimal_steps[label]['steps_X'],
    #         'mrf': optimal_steps[label]['steps_mrf'],
    #     } for label in labels]
    # )
    # for label in labels:
    #     print {
    #         'label': label,
    #         'sigma': optimal_steps[label]['steps_sigma'],
    #         'X': optimal_steps[label]['steps_X'],
    #         'mrf': optimal_steps[label]['steps_mrf'],
    #     }
    #     partial_fusion = partial(label_fusion, input_image=input_image, image_atlas=atlases['WMnMPRAGE_bias_corr'], echo=exec_options['echo'])
    #     label_fusion_args = {
    #         'label_atlas': atlases[label],
    #         'output_label': os.path.join(output_path, label+'.nii.gz'),
    #         'sigma': optimal_steps[label]['steps_sigma'],
    #         'X': optimal_steps[label]['steps_X'],
    #         'mrf': optimal_steps[label]['steps_mrf'],
    #     } 
    #     partial_fusion(**label_fusion_args)

    files = [(os.path.join(temp_path, label+'.nii.gz'), os.path.join(output_path, label+'.nii.gz')) for label in labels]
    if args.right:
        pool.map(flip_lr, files)
        files = [(os.path.join(output_path, label+'.nii.gz'), os.path.join(output_path, label+'.nii.gz')) for label in labels]
    # Resort output to original ordering
    pool.map(parallel_command,
        ['%s %s %s %s' % (os.path.join(this_path, 'tools', 'swapdimlike.py'), in_file, orig_input_image, out_file) for in_file, out_file in files])
    print '--- Finished --- Elapsed: %s' % timedelta(seconds=time.time()-t)


if __name__ == '__main__':
    args = parser.parse_args()
    # print args
    # exec_options.update({'debug': args.debug, 'verbose': args.verbose})
    if args.verbose:
        exec_options['echo'] = True
    if args.debug:
        print 'Debugging mode forces serial execution.'
        # exec_options['echo'] = True
        args.processes = 1
    pool = parallel.BetterPool(args.processes)
    print 'Running with %d processes.' % pool._processes
    # TODO don't hard code this number of processors
    # pool_small = parallel.BetterPool(4)
    # TODO Add path of script to command()
    # os.environ['PATH'] += os.pathsep + os.path.abspath(os.path.dirname(sys.argv[0]))
    if args.tempdir:
        temp_path = args.tempdir
        if not os.path.exists(temp_path):
            print 'Making %s' % os.path.abspath(temp_path)
            os.makedirs(temp_path)
    else:
        temp_path = tempfile.mkdtemp(dir=os.path.dirname(args.output_path))
    try:
        main(args, temp_path, pool)
    finally:
        pool.close()
        # Clean up temp folders
        if not args.debug and not args.tempdir:
            try:
                rmtree(temp_path)
            except OSError as exc:
                if exc.errno != 2:  # Code 2 - no such file or directory
                    raise
