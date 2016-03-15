#!/usr/bin/env python
"""
Wrapper for antsApplyTransforms to make it more like the old WarpImageMultiTransform
COMMAND:
     antsApplyTransforms
          antsApplyTransforms, applied to an input image, transforms it according to a
          reference image and a transform (or a set of transforms).

OPTIONS:
     -d, --dimensionality 2/3
          This option forces the image to be treated as a specified-dimensional image. If
          not specified, antsWarp tries to infer the dimensionality from the input image.

     -e, --input-image-type 0/1/2/3
                            scalar/vector/tensor/time-series
          Option specifying the input image type of scalar (default), vector, tensor, or
          time series.
          <VALUES>: 0

     -i, --input inputFileName
          Currently, the only input objects supported are image objects. However, the
          current framework allows for warping of other objects such as meshes and point
          sets.

     -r, --reference-image imageFileName
          For warping input images, the reference image defines the spacing, origin, size,
          and direction of the output warped image.

     -o, --output warpedOutputFileName
                  [compositeDisplacementField,<printOutCompositeWarpFile=0>]
          One can either output the warped image or, if the boolean is set, one can print
          out the displacement field based on thecomposite transform and the reference
          image.

     -n, --interpolation Linear
                         NearestNeighbor
                         MultiLabel[<sigma=imageSpacing>,<alpha=4.0>]
                         Gaussian[<sigma=imageSpacing>,<alpha=1.0>]
                         BSpline[<order=3>]
                         CosineWindowedSinc
                         WelchWindowedSinc
                         HammingWindowedSinc
                         LanczosWindowedSinc
          Several interpolation options are available in ITK. These have all been made
          available.

     -t, --transform transformFileName
                     [transformFileName,useInverse]
          Several transform options are supported including all those defined in the ITK
          library in addition to a deformation field transform. The ordering of the
          transformations follows the ordering specified on the command line. An identity
          transform is pushed onto the transformation stack. Each new transform
          encountered on the command line is also pushed onto the transformation stack.
          Then, to warp the input object, each point comprising the input object is warped

WarpImageMultiTransform ImageDimension moving_image output_image  -R reference_image --use-NN   SeriesOfTransformations--(See Below)

"""


import os
import sys
import subprocess
import argparse


def parse_transforms(t):
    i = 0
    N = len(t)
    args = []
    while i < N:
        arg = t[i]
        if arg == '-i':
            args.append('[%s,1]' % t[i+1])
            i += 2
        else:
            args.append(t[i])
            i += 1
    return args


antsApplyTransforms = 'antsApplyTransforms'


image_types = ('scalar', 'vector', 'tensor', 'timeseries')
image_type_map = dict(zip(image_types, range(len(image_types))))

parser = argparse.ArgumentParser(description='Wrapper for antsApplyTransforms to make it more like the old WarpImageMultiTransform.')
parser.add_argument('--n_dim', default=None, help='Can be 2 or 3.  This option forces the image to be treated as a specified-dimensional image. If not specified, antsWarp tries to infer the dimensionality from the input image.')
parser.add_argument('moving_image', help='The moving image.')
parser.add_argument('output_image', help='The output image.')
parser.add_argument('reference_image', help='For warping input images, the reference image defines the spacing, origin, size, and direction of the output warped image.')
parser.add_argument('transforms', metavar='transforms', nargs=argparse.REMAINDER, help='A series of transformations.  The -i switch can be used to invert an affine transformation.  Transformations are processed in last-in-first-out order.')
parser.add_argument('-n', '--interpolation', default=None, help='Methods: Linear, NearestNeighbor, MultiLabel[<sigma=imageSpacing>,<alpha=4.0>], Gaussian[<sigma=imageSpacing>,<alpha=1.0>], BSpline[<order=3>], CosineWindowedSinc, WelchWindowedSinc, HammingWindowedSinc, LanczosWindowedSinc')
parser.add_argument('-e', '--input-image-type', default='scalar', choices=image_types, help='Option specifying the input image type.  Defaults to scalar.')
parser.add_argument('--use-NN', action='store_true', help='Use nearest neighbor interpolation.')
parser.add_argument('--use-BSpline', action='store_true', help='Use bicubic interpolation.')
parser.add_argument('--use-ML', default=None, help='<sigma=imageSpacing>,<alpha=4.0>')


if __name__ == '__main__':
    args = parser.parse_args()
    if not args.transforms:
        print 'Must provide transforms'
        sys.exit(1)
    transforms = ' '.join(parse_transforms(args.transforms))
    if args.use_NN:
        interp = 'NearestNeighbor'
    elif args.use_BSpline:
        interp = 'BSpline'
    elif args.use_ML:
        interp = 'MultiLabel' + ('[%s]' % args.use_ML if args.use_ML else '')
    else:
        interp = args.interpolation
    switches = []
    switches.append('d %s' if args.n_dim else '')
    switches.append('-n %s' % interp if interp else '')
    # print args, switches
    cmd = 'antsApplyTransforms -i %s -o %s -r %s %s -t %s' % (args.moving_image, args.output_image, args.reference_image, ' '.join(switches), transforms)
    print cmd
    os.system(cmd)