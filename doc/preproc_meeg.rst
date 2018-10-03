.. _preproc_meeg:

Preprocessing pipeline
**********************

The preprocessing pipeline runs the ICA algorithm for an automatic removal of 
eyes and heart related artefacts. A report is automatically generated and can be used to 
correct and/or fine-tune the correction in each subject (see the example section :ref:`preproc_example`).

The **input** data can be in **ds** or **fif** format. 

The **output** is the **preprocessed data** stored in the workflow directory. It's a good rule
to inspect the report file saved in the same dir to look at the excluded ICA components. It is
also possible to include and exclude more components by using either a jupyter notebook or
the preprocessing pipeline with different flag parameters.

The preprocessing pipeline is implemented by the function :py:func:`create_pipeline_preproc_meeg <ephypype.pipelines.preproc_meeg.create_pipeline_preproc_meeg>`
and its Nodes (:py:class:`ds2fif <ephypype.nodes.import_data.ConvertDs2Fif>`, 
:py:class:`preproc <ephypype.interfaces.mne.preproc.PreprocFif>`,
:py:class:`ica <ephypype.interfaces.mne.preproc.CompIca>`) 
are based on the MNE Python functions performing the decomposition of the MEG/EEG signal using an ICA
algorithm.

.. |here| raw:: html

   <a href="http://martinos.org/mne/stable/auto_tutorials/plot_artifacts_correction_ica.html" target="_blank">here</a>

In particular, the node:
   
* :py:class:`ds2fif <ephypype.nodes.import_data.ConvertDs2Fif>` converts from ds to fif data format 
* :py:class:`preproc <ephypype.interfaces.mne.preproc.PreprocFif>` performs filtering on the raw data
* :py:class:`ica <ephypype.interfaces.mne.preproc.CompIca>` computes ICA solution on raw fif data


.. figure::  ../../img/graph_dot_preproc.jpg
   :scale: 75 %
   :align: center
   
.. note:: An **ICA tutorial** with the main functions used in MNE can be found |here|.
.. seealso:: See :ref:`preproc_example` to get an example on how to write a preprocessing pipeline.







