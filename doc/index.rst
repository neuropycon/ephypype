.. _ephypype:

ephypype
********

The ephypype package includes pipelines for electrophysiology analysis.
It's based mainly on MNE-Python package, as well as more standard python libraries such as Numpy and Scipy.
Current implementations allow for

* MEG/EEG data import
* MEG/EEG data pre-processing and cleaning by an automatic removal of eyes and heart related artifacts
* sensor or source-level connectivity analyses

The ephypype package provides the main pipelines in the :ref:`pipelines`:

* the :ref:`preproc_meeg` runs the ICA algorithm for an automatic removal of eyes and heart related artefacts
* the :ref:`power` computes the power spectral density (PSD) on sensor space
* the :ref:`source_reconstruction` computes the inverse solution starting from raw/epoched data
* the :ref:`spectral_connectivity` perform connectivity analysis in sensor or source space


Pipelines
=========

.. toctree::
   :maxdepth: 3

   pipelines/preproc_meeg
   pipelines/power
   pipelines/source_reconstruction
   pipelines/spectral_connectivity


Installation
============

.. toctree::
   :maxdepth: 1

   includeme

Subpackages
-----------

.. toctree::
   :maxdepth: 1

   ephypype.interfaces
   ephypype.nodes
   ephypype.pipelines


Modules
-------

ephypype.aux_tools
------------------------
.. automodule:: ephypype.aux_tools
    :members:


ephypype.compute_fwd_problem
----------------------------------

.. automodule:: ephypype.compute_fwd_problem
    :members:


ephypype.compute_inv_problem
----------------------------------

.. automodule:: ephypype.compute_inv_problem
    :members:


ephypype.fif2ts
---------------------

.. automodule:: ephypype.fif2ts
    :members:


ephypype.import_ctf
-------------------------


.. automodule:: ephypype.import_ctf
    :members:


ephypype.import_mat
-------------------------

.. automodule:: ephypype.import_mat
    :members:


ephypype.import_txt
-------------------------

.. automodule:: ephypype.import_txt
    :members:


ephypype.power
--------------------

.. automodule:: ephypype.power
    :members:


ephypype.preproc
----------------------

.. automodule:: ephypype.preproc
    :members:


ephypype.spectral
-----------------------

.. automodule:: ephypype.spectral
    :members:

