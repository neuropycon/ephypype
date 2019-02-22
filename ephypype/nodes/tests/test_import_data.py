"""Test import_data."""
import mne
import pytest
import os.path as op
import numpy as np
import scipy.io as sio

import nipype.pipeline.engine as pe

from ephypype.nodes.import_data import ConvertDs2Fif, ImportHdf5, ImportMat
from ephypype.nodes.import_data import Ep2ts, Fif2Array
from ephypype.import_data import write_hdf5

from numpy.testing import assert_array_almost_equal, assert_array_equal

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


def test_ep2ts_node():
    """Test data conversion."""
    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=False,
                           stim=False, exclude='bads')

    # Define and read epochs:
    events = mne.find_events(raw, stim_channel='STI 014')

    # Define epochs parameters:
    event_id = dict(aud_l=1, aud_r=2)  # event trigger and conditions
    tmin = -0.2  # start of each epoch (200ms before the trigger)
    tmax = 0.5  # end of each epoch (500ms after the trigger)

    epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                        picks=picks, baseline=(None, 0), preload=False)

    data = epochs.get_data()
    # Save all epochs in a fif file:
    epo_filename = raw_fname.replace('.fif', '-epo.fif')
    epochs.save(epo_filename)

    # Call Ep2ts node in order to write the timeseries of epoched data in .npy
    ep2ts_node = pe.Node(interface=Ep2ts(), name='ep2ts')
    ep2ts_node.inputs.fif_file = epo_filename

    ep2ts_node.run()

    # check if the node output contains the same data previously created
    npy_filename = ep2ts_node.result.outputs.ts_file
    data_test = np.load(npy_filename)

    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)


def test_fif2array_node():
    """Test data conversion."""
    raw = mne.io.read_raw_fif(raw_fname)

    picks = mne.pick_types(raw.info, meg=True, eeg=False, eog=False,
                           stim=False, exclude='bads')

    data = raw.get_data()[picks, :]
    sfreq = raw.info['sfreq']
    channel_coo = np.array([raw.info['chs'][i]['loc'][:3] for i in picks])
    channel_names = np.array([raw.ch_names[pos] for pos in picks], dtype='str')

    # Call Fif2Array node in order to write the raw timeseries in .npy
    fif2array_node = pe.Node(interface=Fif2Array(), name='fif2array')
    fif2array_node.inputs.fif_file = raw_fname

    fif2array_node.run()

    # check if node outputs contains the same data stored in raw
    npy_filename = fif2array_node.result.outputs.array_file
    data_test = np.load(npy_filename)
    channel_coo_test = np.loadtxt(
        fif2array_node.result.outputs.channel_coords_file)
    channel_names_test = [line.strip() for line in
                          open(fif2array_node.result.outputs.channel_names_file)]  # noqa

    # check the data time series
    assert data.shape == data_test.shape
    assert_array_almost_equal(data, data_test)

    # check the sampling frequency
    assert sfreq == fif2array_node.result.outputs.sfreq

    # check sensor locations and labels
    assert_array_equal(channel_coo, channel_coo_test)
    assert_array_equal(channel_names, channel_names_test)
