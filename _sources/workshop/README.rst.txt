.. _general_workshop:


Workshop at |CuttingEEG|
========================

In this hands-on session we will describe the philosophy, architecture and functionalities of NeuroPycon and provide illustrative examples through interactive notebooks.

We will show how to use NeuroPycon pipeline to analyze EEG (MEG) data with a focus on automatic artifact removal by ICA, ERP components computation and (if times allows) source reconstruction from MEG data.

Basic knowledge of (or a keen interest in) **Python** is required. Furthermore, we suggest the following lectures:

* |Gorgolewski| et al. (2011) Front. Neuroinform. 5:13
* |Gramfort| et al. (2013), Front. Neurosci. 7:267
* |Meunier_Pascarella| et al. (2020), Neuroimage 

.. |CuttingEEG| raw:: html

   <a href="https://cuttingeeg2021.org/" target="_blank">CuttingEEG</a>
   
.. |Gorgolewski| raw:: html

   <a href="https://www.frontiersin.org/articles/10.3389/fninf.2011.00013/full" target="_blank">Gorgolewski</a>

.. |Gramfort| raw:: html

   <a href="https://www.frontiersin.org/articles/10.3389/fnins.2013.00267/full" target="_blank">Gramfort</a>

.. |Meunier_Pascarella| raw:: html

   <a href="https://www.sciencedirect.com/science/article/pii/S1053811920305061" target="_blank">Meunier, Pascarella</a>

   

Installation
------------
We recommend to install neuropycon and the related software (MNE-python, Freesurfer) before the workshop. 

First, we recommend to install MNE python by following the |installation instructions|. The last version of MNE-python relies on python 3.9.

.. |installation instructions| raw:: html

   <a href="https://mne.tools/stable/install/index.html" target="_blank">MNE python installation instructions</a>
   

Alternativaly, you can create an enviroment by Anaconda and install the packages contained in :download:`requirements <https://github.com/neuropycon/ephypype/tree/master/doc/workshop/requirements.txt>` file, e.g.

.. code-block:: bash

        $ conda create -n cuttingeeg python=3.7
        $ pip install -r requirements.txt
        $ pip install jupyter


   
Install ephypype
^^^^^^^^^^^^^^^^
To install ephypype package, download from |github| the last version and install it:

.. code-block:: bash

        $ git clone https://github.com/neuropycon/ephypype.git
        $ cd ephypype
        $ python setup.py develop

.. |github| raw:: html

   <a href="https://github.com/neuropycon/ephypype" target="_blank">github</a>
   
   
Sample data
-----------
During the workshop we use some sample datasets that will be shared on |zenodo|


.. |zenodo| raw:: html

   <a href="https://zenodo.org/communities/cuttingeeg" target="_blank">zenodo</a>

Freesurfer
^^^^^^^^^^

1. Download Freesurfer software:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall
   
   
Notebooks
---------
   
.. toctree::
    :maxdepth: 1
    


