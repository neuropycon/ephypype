"""Test power."""
import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

import os.path as op  # noqa
import mne  # noqa

from ephypype.import_ctf import convert_ds_to_raw_fif  # noqa
from mne.datasets.brainstorm import bst_auditory  # noqa

data_path = bst_auditory.data_path()
ds_fname = op.join(data_path, 'MEG', 'bst_auditory', 'S01_AEF_20131218_01.ds')


def test_convert_ds_to_raw_fif():
    """Test data conversion."""

    raw_fif_file = convert_ds_to_raw_fif(ds_fname)
    mne.io.read_raw_fif(raw_fif_file)
