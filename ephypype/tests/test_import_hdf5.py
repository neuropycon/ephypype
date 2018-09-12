"""Test import_hdf5."""

import mne
import os.path as op

from ephypype.import_hdf5 import write_hdf5, read_hdf5
from numpy.testing import assert_array_almost_equal

data_path = mne.datasets.sample.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_filt-0-40_raw.fif')


def test_read_write_hdf5():
    """Test write hdf5."""

    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    data = raw.get_data(picks=picks, start=0, stop=600)

    hdf5_file = raw_fname.replace('.fif', '.hdf5')
    write_hdf5(hdf5_file, data, dataset_name='data')

    data_test = read_hdf5(hdf5_file, dataset_name='data')

    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)
