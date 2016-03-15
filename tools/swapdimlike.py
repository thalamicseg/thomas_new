#!/usr/bin/env python
"""
Swaps dimension ordering (reslices) of input image to match another.match
"""

import os
import sys
import subprocess

def read_ordering(f):
    p = subprocess.Popen('fslhd %s' % f, stdout=subprocess.PIPE, shell=True)
    s = p.communicate()[0].split('\n')
    order = [el.split()[-1] for el in s if 'qform' in el and 'orient' in el]
    order = [''.join([e[0] for e in el.split('-to-')]) for el in order]
    return order


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print '%s input_nii like_nii output_nii' % sys.argv[0]
        print ' Reorders input_nii to match that of like_nii.'
        sys.exit(0)
    input_file = sys.argv[1]
    like_file = sys.argv[2]
    output_file = sys.argv[3]

    order = read_ordering(like_file)
    os.system('fslswapdim %s %s %s' % (input_file, ' '.join(order), output_file))
