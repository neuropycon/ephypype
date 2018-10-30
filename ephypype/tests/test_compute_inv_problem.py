"""Test compute_inv_problem."""

import mne
from ephypype.compute_inv_problem import compute_noise_cov

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
filter_raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'


def test_compute_noise_cov():
    """Test compute noise covariance data from a continuous segment
    of raw data."""

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    noise_cov_fpath = compute_noise_cov('', segment_raw_fname)

    noise_cov = mne.read_cov(noise_cov_fpath)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == noise_cov['dim']
