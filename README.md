# Description

Neuropycon package of functions for electrophysiology analysis, can be used from
graphpype and nipype


# Documentation

https://neuropycon.github.io/neuropycon_doc/ephypype.html


# Installation

## Requirements
Up to now ephypype works only with python2; python3 compatibility is planned for later releases

* numpy
* scikit-learn
* mne
* nipype
* graphpype

## Install package
### Install ephypype
```bash
git clone https://github.com/neuropycon/ephypype.git
cd ephypype
sudo python setup.py develop
cd ..

```
### Install graphpype
```bash
git clone https://github.com/neuropycon/graphpype.git
cd graphpype
pip install .
cd ..
```

## Software

### Freesurfer

1. Download Freesurfer sotware:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall


### MNE

1. Download MNE sotware:

http://martinos.org/mne/dev/install_mne_c.html

Good practice for developpers:
------------------------------    
    1. Fork the package on your github
    
    2. clone the forked package as origin 
    git clone https://github.com/your_github_login/ephypype.git
    
    3. add neuropycon repo as upstream 
    git remote add upstream  https://github.com/neuropycon/ephypype.git
    
    4. create a new branch before modifying any part of the code, or make a fresh clone, make a branch and report your modifications. The origin checkout as to as as fresh as possible
    git checkout -b my_new_branch
    
    5. commit and the new branch to your forked version of the packages
    git commit -m"My modifications" -a 
    git pull origin my_new_branch
    
    6. make a pull request on neuropycon version of the package
    
    
Magical sentence to modify all the import neuropype_ephy -> ephypype:
-------------------------------------------------------------------    
    
find dir_path -type f -print0 | xargs -0 sed -i 's/old_name/new_name/g'

* example:

find ~/Tools/python/Projects/my_project -type f 
-print0 | xargs -0 sed -i 's/neuropype_ephy/ephypype/g'