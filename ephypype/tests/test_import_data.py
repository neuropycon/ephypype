"""Test import_data."""
import mne
import os.path as op
import numpy as np

import nipype.pipeline.engine as pe

from ephypype.aux_tools import _change_wd
from ephypype.nodes.import_data import ConvertDs2Fif, ImportHdf5
from ephypype.import_data import _write_hdf5

from numpy.testing import assert_array_almost_equal

data_path = mne.datasets.testing.data_path()

ds_fname = op.join(data_path, 'CTF', 'testdata_ctf.ds')
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


def test_convert_ds_to_raw_fif():
    """Test data conversion."""

    _change_wd()

    ds2fif_node = pe.Node(interface=ConvertDs2Fif(), name='ds2fif')
    ds2fif_node.inputs.ds_file = ds_fname

    ds2fif_node.run()

    raw_fif_file = ds2fif_node.result.outputs.fif_file
    mne.io.read_raw_fif(raw_fif_file)


def test_read_write_hdf5():
    """Test write hdf5."""

    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')
    data = raw.get_data(picks=picks, start=0, stop=600)

    hdf5_file = raw_fname.replace('.fif', '.hdf5')
    _write_hdf5(hdf5_file, data, dataset_name='data')

    hdf5_node = pe.Node(interface=ImportHdf5(), name='import_hdf5')
    hdf5_node.inputs.ts_hdf5_file = hdf5_file
    hdf5_node.inputs.data_field_name = 'data'

    hdf5_node.run()

    npy_filename = hdf5_node.result.outputs.ts_file
    data_test = np.load(npy_filename)

    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)
