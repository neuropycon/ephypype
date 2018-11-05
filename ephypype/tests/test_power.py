"""Test power."""
import mne
import os.path as op
from ephypype.power import _compute_and_save_psd
from ephypype.aux_tools import _change_wd


import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


def test_power():
    """Test computing and saving PSD."""

    _change_wd()

    fmin = 0.1
    fmax = 300

    _compute_and_save_psd(raw_fname, fmin, fmax, method='welch')
    _compute_and_save_psd(raw_fname, fmin, fmax, method='multitaper')
