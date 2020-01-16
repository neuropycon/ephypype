.. _neuropycon:

Neuropycon
**********

Neuropycon is an open-source multi-modal brain data analysis kit which provides **Python-based
pipelines** for advanced multi-thread processing of fMRI, MEG and EEG data, with a focus on connectivity
and graph analyses. Neuropycon is based on `Nipype <http://nipype.readthedocs.io/en/latest/#>`_,
a tool developed in fMRI field, which facilitates data analyses by wrapping many commonly-used neuro-imaging software into a common
python framework.

Neuropycon project includes two different packages:

* :ref:`ephypype` based on |MNE python| includes pipelines for electrophysiology analysis
* |graphpype| based on |radatools| includes pipelines for graph theoretical analysis of neuroimaging data


.. |MNE python| raw:: html

   <a href="http://martinos.org/mne/stable/index.html" target="_blank">MNE python</a>

.. |radatools| raw:: html

   <a href="http://deim.urv.cat/~sergio.gomez/radatools.php" target="_blank">radatools</a>

.. |graphpype| raw:: html

   <a href="https://neuropycon.github.io/graphpype/" target="_blank">graphpype</a>

Neuropycon provides a very common and fast framework to develop workflows for advanced analyses, in particular
defines a set of different **pipelines** that can be used stand-alone or as **lego** of a bigger workflow:
the input of a pipeline will be the output of another pipeline.

For each possible workflow the **input data** can be specified in three different ways:

* raw MEG data in **.fif** and **.ds** format
* time series of connectivity matrices in **.mat** (Matlab) or **.npy** (Numpy) format
* connectivity matrices in **.mat** (Matlab) or **.npy** (Numpy) format

.. _lego:

.. figure::  img/tiny_all_input_doors_new.jpg
   :width: 75%
   :align:   center

   Main inputs and subsequent pipeline steps

Each pipeline based on nipype engine is defined by **nodes** connected together,
where each node maybe wrapping of existing software (as MNE-python modules or radatools functions)
as well as providing easy ways to implement function defined by the user.

We also provide neuropycon with a Command Line Interface (**CLI**) that up to now wraps only some of 
the functionality of the ephypype package  but will be expanded in the future. 
A detailed explanation of the command line interface operation principles and examples can be found :ref:`here <neuropycon_cli>`.

.. _ephypype:

ephypype
********

The ephypype package includes pipelines for electrophysiology analysis.
It's based mainly on MNE-Python package, as well as more standard python libraries such as Numpy and Scipy.
Current implementations allow for

* MEG/EEG data import
* MEG/EEG data pre-processing and cleaning by an automatic removal of eyes and heart related artifacts
* sensor or source-level connectivity analyses

The ephypype package provides the following **pipelines**:

* the :ref:`preprocessing pipeline <preproc_meeg>` runs the ICA algorithm for an automatic removal of eyes and heart related artefacts
* the :ref:`power pipeline <power>` computes the power spectral density (PSD) on sensor space
* the :ref:`inverse solution pipeline <source_reconstruction>` computes the inverse solution starting from raw/epoched data
* the :ref:`connectivity pipeline <spectral_connectivity>` perform connectivity analysis in sensor or source space


.. comment:
    Pipelines
    =========
    
    .. toctree::
       :maxdepth: 3
    
       preproc_meeg
       power
       source_reconstruction
       spectral_connectivity


.. _ephy_install:

Installation
=============

ephypype works with **python3**

* mne>0.14
* nipype
* h5py

These dependencies are automatically installed during ephypype installation.

We also recommend to install MNE python by following the |installation instructions|.

.. |installation instructions| raw:: html

   <a href="http://martinos.org/mne/dev/install_mne_python.html#check-your-installation" target="_blank">MNE python installation instructions</a>


Install ephypype
^^^^^^^^^^^^^^^^

.. code-block:: bash

   $ pip install ephypype
    

Freesurfer
^^^^^^^^^^

1. Download Freesurfer software:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall

.. comment:
    .. toctree::
        :maxdepth: 1

        includeme
