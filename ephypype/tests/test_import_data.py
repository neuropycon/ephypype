"""Test import_data."""
import mne
import pytest
import locale
import os.path as op
import numpy as np
import scipy.io as sio

import nipype.pipeline.engine as pe


from ephypype.nodes.import_data import ConvertDs2Fif, ImportHdf5, ImportMat
from ephypype.import_data import write_hdf5

from numpy.testing import assert_array_almost_equal

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
data_path = mne.datasets.testing.data_path()

ds_fname = op.join(data_path, 'CTF', 'testdata_ctf.ds')
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


@pytest.mark.usefixtures("change_wd")
def test_ds2fif_node(change_wd):
    """Test ConvertDs2Fif Node."""
    ds2fif_node = pe.Node(interface=ConvertDs2Fif(), name='ds2fif')
    ds2fif_node.inputs.ds_file = ds_fname

    ds2fif_node.run()

    raw_fif_file = ds2fif_node.result.outputs.fif_file
    mne.io.read_raw_fif(raw_fif_file)


def test_import_hdf5_node():
    """Test ImportHdf5 Node."""

    # write raw data in .hdf5 file
    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')
    data = raw.get_data(picks=picks, start=0, stop=600)

    hdf5_filename = raw_fname.replace('.fif', '.hdf5')
    write_hdf5(hdf5_filename, data, dataset_name='data')

    # test ImportHdf5 Node
    hdf5_node = pe.Node(interface=ImportHdf5(), name='import_hdf5')
    hdf5_node.inputs.ts_hdf5_file = hdf5_filename
    hdf5_node.inputs.data_field_name = 'data'

    hdf5_node.run()

    # check if the node output contains the same data previously created
    npy_filename = hdf5_node.result.outputs.ts_file
    data_test = np.load(npy_filename)

    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)


def test_import_mat_node():
    """Test ImportMat Node."""

    # write raw data in .mat file
    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')
    data = raw.get_data(picks=picks, start=0, stop=600)

    mat_filename = raw_fname.replace('.fif', '.mat')
    sio.savemat(mat_filename, {'data': data})

    # test ImportHdf5 Node
    import_mat_node = pe.Node(interface=ImportMat(), name='import_mat')
    import_mat_node.inputs.tsmat_file = mat_filename
    import_mat_node.inputs.data_field_name = 'data'

    import_mat_node.run()

    # check if the node output contains the same data previously created
    npy_filename = import_mat_node.result.outputs.ts_file
    data_test = np.load(npy_filename)

    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)
