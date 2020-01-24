"""Preprocessing Pipeline."""

# Authors: Dmitrii Altukhov <dm-altukhov@ya.ru>
#          Annalisa Pascarella <a.pascarella@iac.cnr.it>

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface, Function
from ..interfaces.mne.preproc import PreprocFif
from ..interfaces.mne.preproc import CompIca
from ..nodes.import_data import ConvertDs2Fif
from ..preproc import _preprocess_set_ica_comp_fif_to_ts


def get_ext_file(raw_file):
    """Get file extension."""
    from nipype.utils.filemanip import split_filename as split_f

    subj_path, basename, ext = split_f(raw_file)

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
                                 down_sfreq=None, is_ICA=True, variance=0.95,
                                 ECG_ch_name='', EoG_ch_name='', reject=None,
                                 is_set_ICA_components=False,
                                 n_comp_exclude=[], is_sensor_space=True):
    """Preprocessing pipeline.

    Parameters
    ----------
    main_path : str
        main path to of the pipeline
    pipeline_name: str (default 'preproc_meeg')
        name of the pipeline
    data_type: str (default 'fif')
        data type: 'fif' or 'ds'
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

    if data_type == 'ds':
        ds2fif_node = pe.Node(interface=ConvertDs2Fif(), name='ds2fif')
        pipeline.connect(inputnode, 'raw_file', ds2fif_node, 'ds_file')

    # preprocess
    if not is_set_ICA_components:
        preproc_node = pe.Node(interface=PreprocFif(), name='preproc')

        preproc_node.inputs.l_freq = l_freq
        preproc_node.inputs.h_freq = h_freq
        if down_sfreq:
            preproc_node.inputs.down_sfreq = down_sfreq

        if data_type == 'ds':
            pipeline.connect(ds2fif_node, 'fif_file', preproc_node, 'fif_file')
        elif data_type == 'fif':
            pipeline.connect(inputnode, 'raw_file', preproc_node, 'fif_file')

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
            pipeline.connect(inputnode, 'subject_id', ica_node, 'subject_id')

        else:

            ica_node = pe.Node(interface=CompIca(), name='ica')
            ica_node.inputs.n_components = variance
            ica_node.inputs.ecg_ch_name = ECG_ch_name
            ica_node.inputs.eog_ch_name = EoG_ch_name

            if reject:
                ica_node.inputs.reject = reject

            pipeline.connect(preproc_node, 'fif_file', ica_node, 'fif_file')

    return pipeline
