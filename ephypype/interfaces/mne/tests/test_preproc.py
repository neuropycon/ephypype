"""Test preproc."""

import mne
import pytest
import os.path as op
import numpy as np
import nipype.pipeline.engine as pe
from ephypype.interfaces.mne.preproc import CreateEp, PreprocFif, CompIca
from ephypype.interfaces.mne.preproc import DefineEpochs, DefineEvoked
from ephypype.preproc import _preprocess_set_ica_comp_fif_to_ts


import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')
epo_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw-epo.fif')
events_file = op.join(data_path, 'MEG', 'sample',
                      'sample_audvis_trunc_raw-eve.fif')


@pytest.mark.usefixtures("change_wd")
def test_epoching_node():
    """Test epoching node"""
    epoch_node = pe.Node(interface=CreateEp(), name='epoching')
    epoch_node.inputs.ep_length = 1  # split in 1 second epochs
    epoch_node.inputs.fif_file = raw_fname
    epoch_node.run()


@pytest.mark.usefixtures("change_wd")
def test_define_eeg_epochs():
    """Test epoching node"""
    epoch_node = pe.Node(interface=DefineEpochs(), name='epoching')
    epoch_node.inputs.events_file = events_file
    epoch_node.inputs.events_id = {'eve': 1}
    epoch_node.inputs.t_min = -0.1
    epoch_node.inputs.t_max = 1.0
    epoch_node.inputs.fif_file = raw_fname
    epoch_node.inputs.data_type = 'eeg'
    epoch_node.inputs.baseline = (None, 0)
    epoch_node.run()


@pytest.mark.usefixtures("change_wd")
def test_define_epochs():
    """Test epoching node"""
    epoch_node = pe.Node(interface=DefineEpochs(), name='epoching')
    epoch_node.inputs.events_file = events_file
    epoch_node.inputs.events_id = {'eve': 1}
    epoch_node.inputs.t_min = -0.1
    epoch_node.inputs.t_max = 1.0
    epoch_node.inputs.fif_file = raw_fname
    epoch_node.inputs.data_type = 'meg'
    epoch_node.inputs.baseline = (None, 0)
    epoch_node.run()


def test_compute_evoked():
    """Test evoked node"""
    evoked_node = pe.Node(interface=DefineEvoked(), name='evoked')

    evoked_node.inputs.fif_file = epo_fname
    evoked_node.inputs.events_id = {'aud_l': 1, 'aud_r': 2}

    evoked_node.run()
    
    
def test_preprocess_fif():
    """Test filter and downsample raw data."""

    l_freq = 0.1
    h_freq = 40
    down_sfreq = 250

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    # create PreprocFif node
    preproc_node = pe.Node(interface=PreprocFif(), name='preprocess')
    preproc_node.inputs.fif_file = segment_raw_fname
    preproc_node.inputs.l_freq = l_freq
    preproc_node.inputs.h_freq = h_freq
    preproc_node.inputs.down_sfreq = down_sfreq

    preproc_node.run()

    assert preproc_node.result.outputs.fif_file


def test_compute_ica():
    """Test compute ICA on raw data."""

    ecg_ch_name = 'ECG'
    eog_ch_name = ['HEOG, VEOG']
    variance = 0.5
    reject = dict(mag=5e-12, grad=5000e-13)

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    # create CompIca node to compute ica on raw data
    ica_node = pe.Node(interface=CompIca(), name='ica')
    ica_node.inputs.fif_file = segment_raw_fname
    ica_node.inputs.raw_fif_file = segment_raw_fname
    ica_node.inputs.ecg_ch_name = ecg_ch_name
    ica_node.inputs.eog_ch_name = eog_ch_name
    ica_node.inputs.variance = variance
    ica_node.inputs.reject = reject

    ica_node.run()

    assert ica_node.result.outputs.ica_file
    assert ica_node.result.outputs.ica_sol_file
    assert ica_node.result.outputs.ica_ts_file
    assert ica_node.result.outputs.report_file

    raw_cleaned = mne.io.read_raw_fif(ica_node.result.outputs.ica_file)

    assert raw.get_data().shape == raw_cleaned.get_data().shape


def test_set_IC_components():
    """Test compute ICA on raw data."""

    ecg_ch_name = 'ECG'
    eog_ch_name = ['HEOG, VEOG']
    variance = 0.5
    reject = dict(mag=5e-12, grad=5000e-13)

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    # create CompIca node to compute ica on raw data
    ica_node = pe.Node(interface=CompIca(), name='ica')
    ica_node.inputs.fif_file = segment_raw_fname
    ica_node.inputs.raw_fif_file = segment_raw_fname
    ica_node.inputs.ecg_ch_name = ecg_ch_name
    ica_node.inputs.eog_ch_name = eog_ch_name
    ica_node.inputs.variance = variance
    ica_node.inputs.reject = reject

    ica_node.run()

    n_comp_exclude = {'sample': {'run': [0, 1, 2]}}
    ts_file, chs_file, chs_n_file, sf = _preprocess_set_ica_comp_fif_to_ts(
        ica_node.result.outputs.ica_file, 'sample', n_comp_exclude, True)

    assert ts_file
    assert chs_file
    assert chs_n_file
    assert sf

    data = np.load(ts_file)

    idx = mne.pick_types(raw.info, meg=True)
    assert raw.get_data()[idx, :].shape == data.shape
