"""Test compute_inv_problem."""

import mne
import numpy as np
from ephypype.compute_inv_problem import compute_noise_cov
from ephypype.compute_inv_problem import compute_cov_identity

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.sample.data_path()
filter_raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'


def test_compute_noise_cov():
    """Test compute noise covariance data from a continuous segment
    of raw data."""

    # read raw data
    raw = mne.io.read_raw_fif(filter_raw_fname)

    # save short segment of raw data
    segment_raw_fname = filter_raw_fname.replace('raw.fif', '0_10s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=10, overwrite=True)

    noise_cov_fpath = compute_noise_cov('', segment_raw_fname)

    noise_cov = mne.read_cov(noise_cov_fpath)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == noise_cov['dim']


def test_compute_cov_identity():
    """Test compute identity noise covariance data"""

    # compute I
    noise_cov_fpath = compute_cov_identity(filter_raw_fname)
    identity_cov = mne.read_cov(noise_cov_fpath)

    dim = identity_cov['dim']
    assert np.all(identity_cov['data'] == np.identity(dim))

    # read raw data
    raw = mne.io.read_raw_fif(filter_raw_fname)
    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == identity_cov['dim']
