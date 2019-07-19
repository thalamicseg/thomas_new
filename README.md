# THOMAS: Thalamus-Optimized Multi-Atlas Segmentation
Segmentation of the thalamus into 12 nuclei using white-matter-nulled MPRAGE image contrast and PICSL's joint label fusion. Note that this version supports the much faster cropped FOV version (called ST THOMAS in ISMRM abstracts) and the slower original full FOV (THOMAS) using v2 and v0 arguments for -a respectively. 

Temporary Note 7/19/2019: Due to github download bandwidth limitations, some of these files may not show up. We are working on an upgrade which should be within a week.

## Requirements
- [ANTs](https://github.com/ANTsX/ANTs/releases)
- [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- [convert3d](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.C3D)
- [PICSL-MALF](https://www.nitrc.org/frs/?group_id=634)
 

## Installation
- git clone https://github.com/thalamicseg/thomas_new.git
- python require.py

## Usage
- use the thomas_csh wrapper provided (typically this is kept in ~/bin)
  
  Usage: thomas_csh WMnMPRAGE_file \<r\> 

  Note 1: the first argument is the white matter nulled MPRAGE file in NIFTy nii.gz format. Make sure it is just the file name and not a full path (e.g. wmn.nii.gz not ~foo/data/case1/wmn.nii.gz. Basically, run the script in the directory where the file is located. If you have each subject in a directory, go to each directory and call thomas_csh wmn.nii.gz \<r> which can be in a simple csh script
  
  Note 2: the second argument if set to r would also segment the right side (default is left side)
- For full usage of THOMAS, type python THOMAS.py -h
- Example: python THOMAS.py -a v2 -p 4 -v --jointfusion --tempdir temp $1 ALL
	- tempdir is often useful in case something goes wrong, you can resume from previous attempts. Delete this directory if you want to rerun the full segmentation or it will just use the warps from here.
- jointfusion calls the original implementation of the [PICSL MALF algorithm](https://www.nitrc.org/projects/picsl_malf) instead of antsJointFusion.  This was used in the publication.
- swapdimlike.py - reorients an image to match the orientation of another
- form_multiatlas.py - combines many independent labels together into a single atlas
