.. _readme:

.. image:: https://travis-ci.org/neuropycon/ephypype.svg?branch=master
    :target: https://travis-ci.org/neuropycon/ephypype

.. image:: https://codecov.io/gh/neuropycon/ephypype/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/neuropycon/ephypype

.. image:: https://circleci.com/gh/neuropycon/ephypype.svg?style=svg
    :target: https://circleci.com/gh/neuropycon/ephypype

README
******

Description
===========

Neuropycon package of functions for electrophysiology analysis, can be used from
graphpype and nipype

Documentation
=============

https://neuropycon.github.io/ephypype

Installation
=============

Requirements
------------

ephypype works with **python3**

* mne>0.14
* nipype
* configparser
* h5py

These dependencies are automatically installed during ephypype installation (see :ref:`ephy_install`). 

We also recommend to install MNE python by following the |installation instructions|.

.. |installation instructions| raw:: html

   <a href="http://martinos.org/mne/dev/install_mne_python.html#check-your-installation" target="_blank">MNE python</a>

Install package
---------------

.. _ephy_install:

Install ephypype
++++++++++++++++++++++

.. code-block:: bash

    git clone https://github.com/neuropycon/ephypype.git
    cd ephypype
    pip install .
    cd ..


.. comment: 
    .. _conda_install:
   
    Install dependencies with conda
    +++++++++++++++++++++++++++++++

    .. code-block:: bash 

        conda install pandas
        conda install matplotlib


Software
--------

Freesurfer
++++++++++
1. Download Freesurfer software:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall


.. comment:
    MNE
    +++

    1. Download MNE software:

    http://martinos.org/mne/dev/install_mne_c.html
