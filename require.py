#!/usr/bin/env python
"""
Check required dependencies
"""
import os
import sys
import subprocess
import THOMAS_constants


def is_tool(name):
    """
    Function to check if executable can be seen by Python.
    http://stackoverflow.com/a/11210902
    """
    try:
        devnull = open(os.devnull, 'w')
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


executables = {
    'FSL': [
        'fslreorient2std',
        'fslswapdim',
        'fslmaths',
        # 'fslmerge',
        'fslstats',
    ],
    'ANTS': [
        'ANTS',
        'N4BiasFieldCorrection',
        'ComposeMultiTransform',
        'antsApplyTransforms',
        'antsJointFusion',
        'ExtractRegionFromImageByMask',
        'CreateImage',
        'ImageMath',
    ],
    'Convert3D': ['c3d'],
}

flag = False
for toolkit, exe in executables.iteritems():
    for x in filter(lambda el: not is_tool(el), exe):
        print '%s is missing from %s' % (x, toolkit)
        flag = True
if flag:
    sys.exit(1)


if __name__ == '__main__':
    if not flag:
        print 'All required dependencies for THOMAS were found.'
