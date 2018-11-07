"""Test power."""
import mne
import pytest
import os.path as op
from ephypype.power import _compute_and_save_psd


import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


@pytest.mark.usefixtures("change_wd")
def test_power():
    """Test computing and saving PSD."""

    fmin = 0.1
    fmax = 300

    _compute_and_save_psd(raw_fname, fmin, fmax, method='welch')
    _compute_and_save_psd(raw_fname, fmin, fmax, method='multitaper')
