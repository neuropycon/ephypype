"""Test preproc."""

import mne
import os.path as op
import nipype.pipeline.engine as pe
from ephypype.interfaces.mne.preproc import CreateEp
from ephypype.preproc import _preprocess_fif, _compute_ica
from ephypype.aux_tools import _change_wd


import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


def test_epoching_node():
    """Test epoching node"""
    _change_wd()
    epoch_node = pe.Node(interface=CreateEp(), name='epoching')
    epoch_node.inputs.ep_length = 1  # split in 1 second epochs

    epoch_node.inputs.fif_file = raw_fname
    epoch_node.run()


def test_preprocess_fif():
    """Test filter and downsample raw data."""
    _change_wd()

    l_freq = 0.1
    h_freq = 40

    down_sfreq = 250

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    _preprocess_fif(segment_raw_fname, l_freq=l_freq, h_freq=h_freq,
                    down_sfreq=down_sfreq)


def test_compute_ica():
    """Test compute ICA on raw data."""
    _change_wd()

    ecg_ch_name = 'ECG'
    eog_ch_name = 'HEOG, VEOG'
    variance = 25

    reject = dict(mag=5e-12, grad=5000e-13)

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    # compute ica on raw data
    _compute_ica(segment_raw_fname, ecg_ch_name, eog_ch_name, variance, reject)
