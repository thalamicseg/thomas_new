# THOMAS: Thalamus-Optimized Multi-Atlas Segmentation (v 2.0)
Code for segmentation of the thalamus into 12 nuclei using a White-Matter-nulled MPRAGE multi-atlas and PICSL's joint label fusion. Note that this version supports the much faster cropped FOV version (called ST THOMAS in ISMRM abstracts) and the slower original full FOV (THOMAS) using v2 and v0 arguments for -a respectively. 

THOMAS workflow is shown below-
![THOMAS workflow](THOMAS.jpg "Workflow")


## New features
Compared to 1.0, this version  

a. supports  conventional T1 MPRAGE processing (see Usage below)

b. supports  Mac installatios (automatic detection,  PICSL-MALF not required)

c. creates left and right directories for output (bilateral processing is default, see Outputs below) and creates full sized fused labels

## Requirements
- [ANTs](https://github.com/ANTsX/ANTs/releases)
- [FSL](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- [convert3d](http://www.itksnap.org/pmwiki/pmwiki.php?n=Downloads.C3D)
- [PICSL-MALF](https://www.nitrc.org/frs/?group_id=634) (see important note below)
 
Note: you might have to install ITK from scratch to make PICSL-MALF work esp running on CentOS. Ubuntu seems to work fine. MAC users with Mint Linux can use  https://github.com/dzenanz/PICSL_MALF.git for PICSL-MALF and this is compatible with newer ITK versions (e.g. 5.1). If it still fails in jointfusion, edit thomas_csh to remove the --jointfusion option in the three locations and retry. This will force the use of antsJointFusion which is slower but works if ANTS is installed.

## Installation instructions 
- git: due to large files, you will need to install git lfs and then download. Else you will only get soft links and not the actual files. Please email manojsar@email.arizona.edu if you have any issues
- python: run require.py (right now, PYTHON 3 is NOT SUPPORTED so please point python to PYTHON 2 [python2.7 seems to work best])

## Usage
- set an environment variable THOMAS_HOME in .cshrc to where you install thomas (e.g. ~/thomas_new)
- use the thomas_csh wrapper provided for WMn MPRAGE data
  
  Usage: thomas_csh WMnMPRAGE_file \<ro/lo\> 

  Note 1: the first argument is the white matter nulled MPRAGE file in NIFTy nii.gz format. Make sure it is just the file name and not a full path (e.g. wmn.nii.gz not ~foo/data/case1/wmn.nii.gz. Basically, run the script in the directory where the file is located. If you have each subject in a directory, go to each directory and call thomas_csh wmn.nii.gz \<ro/lo> which can be from a simple csh script
    
  Note 2: the second argument if set to ro/lo would only segment the right/left side (default is both left and right)
- use the thomas_csh_mv wrapper provided for standard MPRAGE or T1 (FSPGR in GE) data

  Usage: thomas_csh_mv MPRAGEorT1_file \<ro/lo\> 
  
- For full usage of THOMAS, type python THOMAS.py -h
- Example: python THOMAS.py -a v2 -p 4 -v --jointfusion --tempdir temp wmnmpragefilename ALL
	- tempdir is often useful in case something goes wrong, you can resume from previous attempts. Delete this directory if you want to rerun the full segmentation or it will just use the warps from here.
- jointfusion calls the original implementation of the [PICSL MALF algorithm](https://www.nitrc.org/projects/picsl_malf) instead of antsJointFusion.  This was used in the publication. For MACS, it will skip PICSL due to library issues and just call antsJointFusion which is almost identical but a bit slower.
- swapdimlike.py - reorients an image to match the orientation of another
- form_multiatlas.py - combines many independent labels together into a single atlas
 
## Outputs
The directories named left and right contain the outputs which are individual labels (e.g. 2-AV.nii.gz for anteroventral and so on), thomas.nii.gz which is a single file with all labels fused and thomasfull.nii.gz which is the same size as the input file (i.e. full size as opposed to thomas which is cropped). In addition, nucVols.txt contains the nuclei volumes. regn.nii.gz is the custom template registered to the input image. This file is critical for debugging. Make sure this file and crop_<inputfilename> are well aligned. A color table file called CustomAtlas.ctbl is provided for visualization.

## Thalamic nuclei expansions and label definitions
THOMAS outputs the mammillothalamic tract (14-MTT) and the eleven delineated nuclei are grouped as follows:

	(i) medial group: mediodorsal (12-MD), centromedian (11-CM), habenula (13-Hb) 
	(ii) posterior group: pulvinar (8-Pul), medial geniculate nucleus (10-MGN), lateral geniculate nucleus (9-LGN) 
	(iii) lateral group: ventral posterolateral (7-VPL), ventral lateral anterior (5-VLa), ventral lateral posterior (6-VLp), ventral anterior nucleus (4-VA)
	(iv) anterior group: anteroventral (2-AV)
__Note that 6-VLP is split into 6_VLPv and 6_VLPd. 6_VLPv is the same as VIM used for targeting in DBS applications__

## Citation
The neuroimage paper on THOMAS can be found here https://pubmed.ncbi.nlm.nih.gov/30894331/

	Su J, Thomas FT, Kasoff WS, Tourdias T, Choi EY, Rutt BK, Saranathan M. Thalamus Optimized Multi-atlas Segmentation (THOMAS):
	fast, fully automated segmentation of thalamic nuclei from anatomical MRI. NeuroImage; 194:272-282 (2019)

## Contact
Please contact Manoj Saranathan manojsar@email.arizona.edu in case you have any questions or difficulties in installation/running. 

