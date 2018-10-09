"""Test power."""
import mne
import tempfile
import os
from ephypype.power import compute_and_save_psd

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'


def test_power():
    """Test computing and saving PSD."""

    current_wd = os.getcwd()
    tmp_dir = tempfile.mkdtemp()

    os.chdir(tmp_dir)

    fmin = 0.1
    fmax = 300

    compute_and_save_psd(raw_fname, fmin, fmax, method='welch')
    compute_and_save_psd(raw_fname, fmin, fmax, method='multitaper')

    os.chdir(current_wd)
