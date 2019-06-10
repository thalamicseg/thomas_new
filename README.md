# THOMAS: Thalamus-Optimized Multi-Atlas Segmentation
Segmentation of the thalamus into 12 nuclei using white-matter-nulled MPRAGE image contrast and PICSL's joint label fusion. Note that this version supports the much faster cropped FOV version (called ST THOMAS in ISMRM abstracts) and the slower original full FOV (THOMAS) using v2 and v0 arguments for -a respectively. 

## Requirements
- [ANTs](https://github.com/ANTsX/ANTs/releases)
- [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- [convert3d](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.C3D)
- [PICSL-MALF](https://www.nitrc.org/frs/?group_id=634)
 

## Installation
- git clone https://github.com/thalamicseg/thomas_new.git
- python require.py

## Usage
- use the thomas_csh wrapper provided (typically put this in ~/bin)
  
  Usage: thomas_csh \<WMn MPRAGE file\> \<r\> 
	Note: the second argument if r would also segment the right side (default is left side)
- For full usage of THOMAS, type python THOMAS.py -h
- Example: python THOMAS.py -a v2 -p 4 -v --jointfusion --tempdir temp $1 ALL
	- tempdir is often useful in case something goes wrong, you can resume from previous attempts. Delete this directory if you want to rerun the full segmentation or it will just use the warps from here.
- jointfusion calls the original implementation of the [PICSL MALF algorithm](https://www.nitrc.org/projects/picsl_malf) instead of antsJointFusion.  This was used in the publication.
- swapdimlike.py - reorients an image to match the orientation of another
- form_multiatlas.py - combines many independent labels together into a single atlas
