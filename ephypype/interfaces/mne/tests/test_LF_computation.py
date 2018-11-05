"""Test LF computation Interface."""

import mne
import nipype.pipeline.engine as pe
import os.path as op
from ephypype.interfaces.mne.LF_computation import LFComputation


data_path = mne.datasets.sample.data_path()
sbj_id = 'sample'
subjects_dir = op.join(data_path, 'subjects')
raw_fname = op.join(data_path, 'MEG', sbj_id,
                    'sample_audvis_raw.fif')


def test_LFComputation():
    """Test LF interface."""

    lf_node = pe.Node(interface=LFComputation(), name='LF')
    lf_node.inputs.sbj_id = 'sample'
    lf_node.inputs.subjects_dir = subjects_dir
    lf_node.inputs.raw_fname = raw_fname
    lf_node.inputs.spacing = 'oct-6'

    lf_node.run()
