# THOMAS: Thalamus-Optimized Multi-Atlas Segmentation
Segmentation of the thalamus into 12 nuclei using the white-matter-nulled image contrast and PICSL's joint label fusion.  

## Requirements
- [ANTs](https://github.com/ANTsX/ANTs/releases)
- [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- [convert3d](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.C3D)
- [picsl-MALF] (https://www.nitrc.org/frs/?group_id=634) 

## Installation
- git clone https://github.com/thalamicseg/thomas.git
- Extract THOMAS-priors.zip to thomas/
- python require.py

## Usage
- use the stthomas wrapped provided (install in ~/bin)
  Usage: stthomas \<WMn MPRAGE file\> \<r\> 
	Note: the second argument if r would also segment the right side (default is left side)
- Example: python THOMAS_v0.py -p 4 --tempdir ants --jointfusion image.nii.gz ./ ALL
	- tempdir is often useful in case something goes wrong, you can resume from previous attempts.
	- jointfusion calls the original implementation of the [PICSL MALF algorithm](https://www.nitrc.org/projects/picsl_malf) instead of antsJointFusion.  This was used in the publication.
- swapdimlike.py - reorients an image to match the orientation of another
- form_multiatlas.py - combines many independent labels together into a single atlas
