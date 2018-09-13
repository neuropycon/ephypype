"""Test power."""
import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

import mne  # noqa

from ephypype.preproc import preprocess_fif, compute_ica  # noqa

data_path = mne.datasets.sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_raw.fif'
filter_raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'


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

    preprocess_fif(segment_raw_fname, l_freq=l_freq, h_freq=h_freq,
                   down_sfreq=down_sfreq)


def test_compute_ica():
    """Test compute ICA on raw data."""
    ECG_ch_name = 'ECG'
    EoG_ch_name = 'HEOG, VEOG'
    variance = 0.95

    reject = dict(mag=5e-12, grad=5000e-13)

    # read raw data
    raw = mne.io.read_raw_fif(raw_fname)

    # save short segment of raw data
    segment_raw_fname = raw_fname.replace('raw.fif', '0_60s_raw.fif')
    raw.save(segment_raw_fname, tmin=0, tmax=60, overwrite=True)

    # compute ica on raw data
    compute_ica(segment_raw_fname, ECG_ch_name, EoG_ch_name, variance, reject)
