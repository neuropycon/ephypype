"""Test power."""
import mne
from ephypype.power import compute_and_save_psd
from ephypype.aux_tools import _change_wd

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'


def test_power():
    """Test computing and saving PSD."""

    _change_wd()

    fmin = 0.1
    fmax = 300

    compute_and_save_psd(raw_fname, fmin, fmax, method='welch')
    compute_and_save_psd(raw_fname, fmin, fmax, method='multitaper')
