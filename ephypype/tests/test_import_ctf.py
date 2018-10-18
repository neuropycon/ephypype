"""Test import_ctf."""
import mne
import os

from ephypype.aux_tools import _change_wd
from ephypype.import_ctf import convert_ds_to_raw_fif  # noqa

data_path = mne.datasets.testing.data_path()
ds_fname = os.path.join(data_path, 'CTF', 'testdata_ctf.ds')


def test_convert_ds_to_raw_fif():
    """Test data conversion."""

    _change_wd()

    raw_fif_file = convert_ds_to_raw_fif(ds_fname)
    mne.io.read_raw_fif(raw_fif_file)
