


FACE dataset
^^^^^^^^^^^^

These examples demonstrate how to process 1 participant of the |FACE| dataset from |Wakeman_Henson|. The data consist of simultaneous MEG/EEG recordings
from 19 healthy participants performing a visual recognition task. Subjects were presented images of famous, unfamiliar and scrambled faces.
Each subject participated in 6 runs, each 7.5 min in duration.

.. |FACE| raw:: html
        
        <a href="https://openneuro.org/datasets/ds000117/versions/1.0.4" target="_blank">FACE</a>

.. |Wakeman_Henson| raw:: html
        
        <a href="https://www.nature.com/articles/sdata20151" target="_blank">Wakeman and
 Henson (2015)</a>

Here, we focus only on MEG data and use :func:`~ephypype.pipelines.create_pipeline_preproc_meeg` to preprocess the MEG raw data and :func:`~ephypype.pipelines.create_pipeline_source_reconstruction` to perform source reconstruction of time-locked event-related fields.
