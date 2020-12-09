"""
Paths, names, optimized hyper-parameters, and other constants for THOMAS.
"""
import os
import shelve


image_name = 'WMnMPRAGE_bias_corr.nii.gz'
# Find path for priors
this_path = os.path.dirname(os.path.realpath(__file__))
orig_template = os.path.join(this_path, 'origtemplate.nii.gz')
assert os.path.exists(orig_template)
template_61 = os.path.join(this_path, 'templ_61x91x62.nii.gz')
assert os.path.exists(template_61)
template_93 = os.path.join(this_path, 'templ_93x187x68.nii.gz')
assert os.path.exists(template_93)
template_93b = os.path.join(this_path, 'p15_templ_93x187x68.nii.gz')
assert os.path.exists(template_93b)
mask_61 = os.path.join(this_path, 'mask_templ_61x91x62.nii.gz')
assert os.path.exists(mask_61)
mask_93 = os.path.join(this_path, 'mask_templ_93x187x68.nii.gz')
assert os.path.exists(mask_93)
mask_93b = os.path.join(this_path, 'mask_templ_93x187x68_p15.nii.gz')
assert os.path.exists(mask_93b)
prior_path = os.path.join(this_path, 'priors/')
assert os.path.exists(prior_path)
subjects = [el for el in os.listdir(prior_path) if os.path.isdir(os.path.join(prior_path, el)) and not el.startswith('.')]
assert len(subjects) > 0

# Names for command-line options and label filenmaes
roi = {
    'param_all': 'ALL',  # special keyword to select all the rois
    'param_names': ('thalamus', 'av', 'va', 'vla', 'vlp', 'vpl', 'vl', 'pul', 'lgn', 'mgn', 'cm', 'md', 'hb', 'mtt'),
    'label_names': ('1-THALAMUS', '2-AV', '4-VA', '5-VLa', '6-VLP', '7-VPL', '4567-VL', '8-Pul', '9-LGN', '10-MGN', '11-CM', '12-MD-Pf', '13-Hb', '14-MTT'),
    }
roi_choices = (roi['param_all'],)+roi['param_names']

# Optimized hyper-parameters for PICSL
db = shelve.open(os.path.join(this_path, 'cv_optimal_picsl_parameters.shelve'), 'r')
optimal = dict(db)
db.close()


if __name__ == '__main__':
    print subjects
    print optimal
