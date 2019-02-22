"""Test Inverse_solution Interface."""

import mne
import pickle
import nipype.pipeline.engine as pe
import numpy as np
import os.path as op
from ephypype.interfaces.mne.Inverse_solution import InverseSolution

from numpy.testing import assert_array_almost_equal


data_path = mne.datasets.testing.data_path()
sbj = 'sample'
subjects_dir = op.join(data_path, 'subjects')
raw_fname = op.join(data_path, 'MEG', sbj, 'sample_audvis_trunc_raw.fif')
fwd_fname = op.join(data_path, 'MEG', sbj,
                    'sample_audvis_trunc_raw-oct-6-fwd.fif')
cov_fname = op.join(data_path, 'MEG', sbj, 'sample_audvis_trunc-cov.fif')


def test_mne_inverse_solution():
    """Test compute MNE inverse solution."""

    inverse_node = pe.Node(interface=InverseSolution(), name='inverse')
    inverse_node.inputs.sbj_id = 'sample'
    inverse_node.inputs.subjects_dir = subjects_dir
    inverse_node.inputs.raw_filename = raw_fname
    inverse_node.inputs.fwd_filename = fwd_fname
    inverse_node.inputs.cov_filename = cov_fname

    inverse_node.run()

    # test that the number of labels matches with 'aparc' annotation and the
    # number of time points with the ones of raw
    assert inverse_node.result.outputs.ts_file
    data = np.load(inverse_node.result.outputs.ts_file)

    labels = mne.read_labels_from_annot(sbj, parc='aparc',
                                        subjects_dir=subjects_dir)

    assert data.shape[1] == len(labels)

    raw = mne.io.read_raw_fif(raw_fname)
    assert data.shape[2] == len(raw.times)

    # check if the labels file were created
    assert inverse_node.result.outputs.labels
    assert inverse_node.result.outputs.label_names
    assert inverse_node.result.outputs.label_coords

    label_names = [line.strip() for line in
                   open(inverse_node.result.outputs.label_names)]
    assert data.shape[1] == len(label_names)

    label_coo = np.loadtxt(inverse_node.result.outputs.label_coords)
    assert label_coo.shape[1] == 3

    with open(inverse_node.result.outputs.labels, 'rb') as f:
        roi = pickle.load(f)

    assert data.shape[1] == len(roi['ROI_names'])
    assert label_names == roi['ROI_names']

    assert len(roi['ROI_coords']) == len(roi['ROI_names'])
    assert len(roi['ROI_colors']) == len(roi['ROI_colors'])

    assert np.concatenate(roi['ROI_coords']).shape[1] == 3
    assert_array_almost_equal(np.concatenate(roi['ROI_coords']), label_coo)


def test_fixed_mne_inverse_solution():
    """Test compute MNE inverse solution."""

    inverse_node = pe.Node(interface=InverseSolution(), name='inverse')
    inverse_node.inputs.sbj_id = 'sample'
    inverse_node.inputs.subjects_dir = subjects_dir
    inverse_node.inputs.raw_filename = raw_fname
    inverse_node.inputs.fwd_filename = fwd_fname
    inverse_node.inputs.cov_filename = cov_fname
    inverse_node.inputs.is_fixed = True

    inverse_node.run()

    assert inverse_node.result.outputs.ts_file


def test_mne_inverse_solution_epoched_data():
    """Test compute MNE inverse solution."""

    # create epoched data
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
    # Save all epochs in a fif file:
    epo_fname = raw_fname.replace('.fif', '-epo.fif')
    epochs.save(epo_fname)

    inverse_node = pe.Node(interface=InverseSolution(), name='inverse')
    inverse_node.inputs.sbj_id = 'sample'
    inverse_node.inputs.subjects_dir = subjects_dir
    inverse_node.inputs.raw_filename = epo_fname
    inverse_node.inputs.fwd_filename = fwd_fname
    inverse_node.inputs.cov_filename = cov_fname
    inverse_node.inputs.is_epoched = True

    inverse_node.run()

    assert inverse_node.result.outputs.ts_file

    # check if data contains the same number of epochs as epo_fname
    data = np.load(inverse_node.result.outputs.ts_file)

    epochs = mne.read_epochs(epo_fname)

    assert data.shape[0] == epochs.events.shape[0]
    assert data.shape[2] == epochs.get_data().shape[2]
