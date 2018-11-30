"""Test InverseSolution Interface."""

import mne
import nipype.pipeline.engine as pe
import os.path as op
from ephypype.interfaces.mne.Inverse_solution import InverseSolution


data_path = mne.datasets.testing.data_path()
sbj_id = 'sample'
subjects_dir = op.join(data_path, 'subjects')
raw_fname = op.join(data_path, 'MEG', sbj_id, 'sample_audvis_trunc_raw.fif')
fwd_fname = op.join(data_path, 'MEG', sbj_id,
                    'sample_audvis_trunc_raw-oct-6-fwd.fif')
events_file = op.join(data_path, 'MEG', sbj_id,
                      'sample_audvis_trunc_raw-eve.fif')
cov_fname = op.join(data_path, 'MEG', sbj_id, 'sample_audvis-cov.fif')


def test_LFComputation():
    """Test LF interface."""

    inverse_node = pe.Node(interface=InverseSolution(), name='inverse')
    inverse_node.inputs.sbj_id = 'sample'
    inverse_node.inputs.subjects_dir = subjects_dir
    inverse_node.inputs.raw_filename = raw_fname
    inverse_node.inputs.fwd_filename = fwd_fname
    inverse_node.inputs.is_epoched = True
    inverse_node.inputs.events_file = events_file
    inverse_node.inputs.events_id = {'aud': 1}
    inverse_node.inputs.t_min = -0.2
    inverse_node.inputs.t_max = 0.5
    inverse_node.inputs.cov_filename = cov_fname

    inverse_node.run()
