.. _power:

Power pipeline
**************

The power pipeline computes the power spectral density (PSD) on epochs or raw data
on **sensor space** or **source space**. The **mean PSD** for each selected 
frequency band is also computed and saved in a numpy file.

The input data shoud be in **fif** or numpy format. 

The outputs are the **psd tensor and frequencies in .npz format** and the **mean PSD in .npy format**
stored in the workflow directory. 

The power pipeline in the **sensor space** is implemented by the function 
:py:func:`create_pipeline_power <ephypype.pipelines.power.create_pipeline_power>`
and its Node :py:class:`power <ephypype.interfaces.mne.power.Power>`
wraps the MNE Python functions  |welch|, |multitaper| computing the PSD
using Welch's method and multitapers respectively.

The power pipeline in the **source space** is implemented by the function 
:py:func:`create_pipeline_power_src_space <ephypype.pipelines.power.create_pipeline_power_src_space>`
and its Node :py:class:`power <ephypype.interfaces.mne.power.Power>` compute the PSD by the welch function
of the scipy package.



.. figure::  ../../img/graph_dot_power.jpg
   :scale: 75 %
   :align: center
   

.. seealso:: See :ref:`power_example` to get an example on how to write a power pipeline in the **sensor space**.


.. |welch| raw:: html

   <a href="http://martinos.org/mne/stable/generated/mne.time_frequency.psd_welch.html#mne.time_frequency.psd_welch" target="_blank">mne.time_frequency.psd_welch</a>


.. |multitaper| raw:: html

   <a href="http://martinos.org/mne/stable/generated/mne.time_frequency.psd_multitaper.html#mne.time_frequency.psd_multitaper" target="_blank">mne.time_frequency.psd_multitaper</a>
   





