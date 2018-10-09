"""Test import_ctf."""
import mne
import tempfile
import os

from ephypype.import_ctf import convert_ds_to_raw_fif  # noqa

data_path = mne.datasets.testing.data_path()
ds_fname = os.path.join(data_path, 'CTF', 'testdata_ctf.ds')


def test_convert_ds_to_raw_fif():
    """Test data conversion."""

    current_wd = os.getcwd()
    tmp_dir = tempfile.mkdtemp()

    os.chdir(tmp_dir)

    raw_fif_file = convert_ds_to_raw_fif(ds_fname)
    mne.io.read_raw_fif(raw_fif_file)

    os.chdir(current_wd)
