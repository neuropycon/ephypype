.. _readme:

README
******

Description
===========

Neuropycon package of functions for electrophysiology analysis, can be used from
graphpype and nipype


..
    Documentation
    =============

    https://annapasca.github.io/neuropype/ephypype/ephypype.html


Installation
=============

Requirements
------------

ephypype works both with **python2** and **python3**

* numpy
* scikit-learn
* ipywidgets
* matplotlib
* pandas
* mne
* nipype
* graphpype

Some of these dependencies you should install manually (see :ref:`conda_install`), others are installed automatically
during ephypype installation (see :ref:`ephy_install`).
To install graphpype see :ref:`graph_install`. 

We also recommend to install the  development master version of |MNE install| (see :ref:`mne_install`).

.. |MNE install| raw:: html

   <a href="http://martinos.org/mne/dev/install_mne_python.html#check-your-installation" target="_blank">MNE python</a>

.. note:: If you have Anaconda it is possible to create an environment using python2 by the command
	``conda create -n py27 python=2.7 ipykernel``

.. warning:: We also recommend to use the nipype version 0.13
	``pip install nipype==0.13``
   
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


.. _graph_install:

Install graphpype
+++++++++++++++++++++++

.. code-block:: bash 

    git clone https://github.com/neuropycon/graphpype.git
    cd graphpype
    pip install .
    cd ..

see |README_graph| for more information.

.. |README_graph| raw:: html

   <a href="https://github.com/neuropycon/graphpype/blob/master/README.md" target="_blank">README</a>


.. _mne_install:
   
Install MNE python
++++++++++++++++++

.. code-block:: bash 

    git clone git://github.com/mne-tools/mne-python.git
    cd mne-python
    sudo python setup.py develop
    cd ..

see |MNE install| for more information.


.. _conda_install:
   
Install dependencies with conda
+++++++++++++++++++++++++++++++

.. code-block:: bash 

    conda install pandas
    conda install ipywidgets
    conda install matplotlib


Software
--------

Freesurfer
++++++++++
1. Download Freesurfer software:

https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

2. Follow the Installation instructions

https://surfer.nmr.mgh.harvard.edu/fswiki/LinuxInstall


MNE
+++

1. Download MNE software:

http://martinos.org/mne/dev/install_mne_c.html

