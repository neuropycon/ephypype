"""Preprocessing Pipeline."""

# Authors: Dmitrii Altukhov <dm-altukhov@ya.ru>
#          Annalisa Pascarella <a.pascarella@iac.cnr.it>
#          David Meunier <david_meunier_79@hotmail.fr>

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.utils.filemanip import split_filename

from ..interfaces.mne.preproc import PreprocFif
from ..interfaces.mne.preproc import CompIca
from ..nodes.import_data import ConvertDs2Fif
from ..preproc import _preprocess_set_ica_comp_fif_to_ts
from ..interfaces.mne.preproc import DefineEpochs, DefineEvoked


def get_ext_file(raw_file):
    """Get file extension."""
    subj_path, basename, ext = split_filename(raw_file)

    print(raw_file)
    is_ds = False
    if ext == 'ds':
        is_ds = True
        return is_ds
    elif ext == 'fif':
        return is_ds
    else:
        raise RuntimeError('only fif and ds file format!!!')


# is_ICA=True                 => apply ICA to automatically remove ECG and EoG
#                                artifacts
# is_set_ICA_components=False => specify all subject_ids and sessions
# is_set_ICA_components=True  => specify the dataset for we want to recompute
#                               the ICA
# in Elekta data, ICA routine automatically looks for EEG61, EEG62


def create_pipeline_preproc_meeg(main_path, pipeline_name='preproc_meeg_pipeline',  # noqa
                                 data_type='fif', l_freq=1, h_freq=150,
                                 down_sfreq=None, is_ICA=True, variance=None,
                                 n_components=None,
                                 ECG_ch_name='', EoG_ch_name='', reject=None,
                                 is_set_ICA_components=False, mapnode=False,
                                 n_comp_exclude=[], is_sensor_space=True,
                                 montage=None, misc=None, bipolar=None,
                                 ch_new_names=None):
    """Preprocessing pipeline.

    Parameters
    ----------
    main_path : str
        main path to of the pipeline
    pipeline_name: str (default 'preproc_meeg')
        name of the pipeline
    data_type: str (default 'fif')
        data type: MEG ('fif', 'ds') or EEG ('eeg') data
    l_freq: float (default 1)
        low cut-off frequency in Hz
    h_freq: float (default 150)
        high cut-off frequency in Hz
    down_sfreq: float (default 300)
        sampling frequency at which the data are downsampled
    is_ICA : boolean (default True)
        if True apply ICA to automatically remove ECG and EoG artifacts
    variance: float (default 0.95)
        float between 0 and 1: the ICA components will be selected by the
        cumulative percentage of explained variance
    ECG_ch_name: str (default '')
        the name of ECG channels
    EoG_ch_name: str (default '')
        the name of EoG channels
    reject: dict | None
        rejection parameters based on peak-to-peak amplitude. Valid keys
        are 'grad' | 'mag' | 'eeg' | 'eog' | 'ecg'. If reject is None then
        no rejection is done
    is_set_ICA_components: boolean (default False)
        set to True if we had the ICA of the raw data, checked the Report
        and want to exclude some ICA components based on their topographies
        and time series
        if True, we have to fill the dictionary variable n_comp_exclude
    n_comp_exclude: dict
        if is_set_ICA_components=True, it has to be a dict containing for
        each subject and for each session the components to be excluded
    is_sensor_space: boolean (default True)
        True if we perform the analysis in sensor space and we use the
        pipeline as lego with the connectivity or inverse pipeline

    raw_file (inputnode): str
        path to raw meg data in fif format
    subject_id (inputnode): str
        subject id

    Outputs
    -------
    pipeline : instance of Workflow
    """

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    print(('*** main_path -> %s' % main_path + ' ***'))
    
    # define the inputs of the pipeline
    inputnode = pe.Node(IdentityInterface(fields=['raw_file', 'subject_id']),
                        name='inputnode')

    if mapnode:

        if data_type == 'ds':
            ds2fif_node = pe.MapNode(interface=ConvertDs2Fif(),
                                     iterfield=['ds_file'], name='ds2fif')
            pipeline.connect(inputnode, 'raw_file', ds2fif_node, 'ds_file')

        # preprocess
        if not is_set_ICA_components:
            preproc_node = pe.MapNode(interface=PreprocFif(),
                                      iterfield=['fif_file'], name='preproc')

            preproc_node.inputs.l_freq = l_freq
            preproc_node.inputs.h_freq = h_freq
            if down_sfreq:
                preproc_node.inputs.down_sfreq = down_sfreq
            if data_type:
                preproc_node.inputs.data_type = data_type

            if data_type == 'ds':
                pipeline.connect(ds2fif_node, 'fif_file',
                                 preproc_node, 'fif_file')
            elif data_type == 'fif':
                pipeline.connect(inputnode, 'raw_file',
                                 preproc_node, 'fif_file')

        if is_ICA:
            if is_set_ICA_components:
                inp = ['fif_file', 'subject_id', 'n_comp_exclude',
                       'is_sensor_space']
                out = ['out_file', 'channel_coords_file', 'channel_names_file',
                       'sfreq']
                fcn = _preprocess_set_ica_comp_fif_to_ts
                ica_node = pe.MapNode(interface=Function(input_names=inp,
                                                         output_names=out,
                                                         function=fcn),
                                      iterfield=['fif_file'],
                                      name='ica_set_comp')

                ica_node.inputs.n_comp_exclude = n_comp_exclude
                ica_node.inputs.is_sensor_space = is_sensor_space

                pipeline.connect(inputnode, 'raw_file', ica_node, 'fif_file')
                pipeline.connect(inputnode, 'subject_id',
                                 ica_node, 'subject_id')

            else:

                ica_node = pe.MapNode(interface=CompIca(),
                                      iterfield=['fif_file', 'raw_fif_file'],
                                      name='ica')
                if variance:
                    ica_node.inputs.variance = variance
                elif n_components:
                    ica_node.inputs.n_components = n_components
                ica_node.inputs.ecg_ch_name = ECG_ch_name
                ica_node.inputs.eog_ch_name = EoG_ch_name

                if reject:
                    ica_node.inputs.reject = reject

                pipeline.connect(preproc_node, 'fif_file',
                                 ica_node, 'fif_file')

                if data_type == 'ds':
                    pipeline.connect(ds2fif_node, 'fif_file',
                                     ica_node, 'raw_fif_file')
                elif data_type == 'fif':
                    pipeline.connect(inputnode, 'raw_file',
                                     ica_node, 'raw_fif_file')

    else:

        if data_type == 'ds':
            ds2fif_node = pe.Node(interface=ConvertDs2Fif(), name='ds2fif')
            pipeline.connect(inputnode, 'raw_file', ds2fif_node, 'ds_file')

        # preprocess
        if not is_set_ICA_components:
            preproc_node = pe.Node(interface=PreprocFif(), name='preproc')

            preproc_node.inputs.l_freq = l_freq
            if h_freq:
                preproc_node.inputs.h_freq = h_freq
            preproc_node.inputs.data_type = data_type

            if down_sfreq:
                preproc_node.inputs.down_sfreq = down_sfreq

            if data_type == 'ds':
                pipeline.connect(ds2fif_node, 'fif_file',
                                 preproc_node, 'fif_file')
            elif data_type == 'eeg':
                preproc_node.inputs.montage = montage
                if bipolar:
                    preproc_node.inputs.bipolar = bipolar
                if misc:
                    preproc_node.inputs.misc = misc
                if ch_new_names:
                    preproc_node.inputs.ch_new_names = ch_new_names
                preproc_node.inputs.eog = EoG_ch_name
                pipeline.connect(inputnode, 'raw_file',
                                 preproc_node, 'fif_file')
            elif data_type == 'fif':
                pipeline.connect(inputnode, 'raw_file',
                                 preproc_node, 'fif_file')

        if is_ICA:
            if is_set_ICA_components:
                inp = ['fif_file', 'subject_id', 'n_comp_exclude',
                       'is_sensor_space']
                out = ['out_file', 'channel_coords_file', 'channel_names_file',
                       'sfreq']
                fcn = _preprocess_set_ica_comp_fif_to_ts
                ica_node = pe.Node(interface=Function(input_names=inp,
                                                      output_names=out,
                                                      function=fcn),
                                   name='ica_set_comp')

                ica_node.inputs.n_comp_exclude = n_comp_exclude
                ica_node.inputs.is_sensor_space = is_sensor_space

                pipeline.connect(inputnode, 'raw_file', ica_node, 'fif_file')
                pipeline.connect(inputnode, 'subject_id',
                                 ica_node, 'subject_id')

            else:

                ica_node = pe.Node(interface=CompIca(), name='ica')
                if variance:
                    ica_node.inputs.variance = variance
                elif n_components:
                    ica_node.inputs.n_components = n_components

                ica_node.inputs.ecg_ch_name = ECG_ch_name
                ica_node.inputs.eog_ch_name = EoG_ch_name
                ica_node.inputs.data_type = data_type

                if reject:
                    ica_node.inputs.reject = reject

                pipeline.connect(preproc_node, 'fif_file',
                                 ica_node, 'fif_file')
                if data_type == 'ds':
                    pipeline.connect(ds2fif_node, 'fif_file',
                                     ica_node, 'raw_fif_file')
                elif data_type == 'fif':
                    pipeline.connect(inputnode, 'raw_file',
                                     ica_node, 'raw_fif_file')
                elif data_type == 'eeg':
                    pipeline.connect(preproc_node, 'fif_file',
                                     ica_node, 'raw_fif_file')

    return pipeline


def create_pipeline_evoked(main_path, pipeline_name='ERP_pipeline',
                           events_id={}, condition=None,
                           decim=1, t_min=None, t_max=None, baseline=None,
                           data_type='meg'):
    """Evoked pipeline.

    Compute time-locked event-related fields/potentials.

    Parameters
    ----------
    main_path : str
        the main path of the workflow
    pipeline_name : str (default ERP_pipeline)
        name of the pipeline
    is_epoched : bool (default False)
        if True and events_id = None the input data are epoch data
        in the format -epo.fif
        if True and events_id is not None, the raw data are epoched
        according to events_id and t_min and t_max values
    events_id: dict (default None)
        the dict of events
    t_min, t_max: int (defualt None)
        define the time interval in which to epoch the raw data
    is_evoked: bool (default False)
        if True the raw data will be averaged according to the events
        contained in the dict events_id
    decim: int
        factor by which to downsample the data
    baseline: tuple
        baseline
    data_type: str
        'meg' or 'eeg'

    raw (inputnode): str
        path to raw data in fif format
    sbj_id (inputnode): str
        subject id

    Returns
    -------
    pipeline : instance of Workflow
    """

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    inputnode = pe.Node(IdentityInterface(
        fields=['sbj_id', 'raw', 'events_file']),
        name='inputnode')

    # Create epochs based on events_id
    assert events_id != {}
    define_epochs = pe.Node(interface=DefineEpochs(), name='define_epochs')
    define_epochs.inputs.events_id = events_id
    define_epochs.inputs.t_min = t_min
    define_epochs.inputs.t_max = t_max
    define_epochs.inputs.decim = decim
    # define_epochs.inputs.events_file = events_file
    define_epochs.inputs.data_type = data_type

    if baseline:
        define_epochs.inputs.baseline = baseline

    pipeline.connect(inputnode, 'raw', define_epochs, 'fif_file')
    pipeline.connect(inputnode, 'events_file', define_epochs, 'events_file')

    compute_evoked = pe.Node(interface=DefineEvoked(), name='compute_evoked')
    compute_evoked.inputs.events_id = events_id
    compute_evoked.inputs.condition = condition

    pipeline.connect(define_epochs, 'epo_fif_file',
                     compute_evoked, 'fif_file')

    return pipeline
