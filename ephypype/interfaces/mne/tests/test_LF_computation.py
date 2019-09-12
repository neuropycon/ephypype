"""Test LF computation Interface."""

import mne
import nipype.pipeline.engine as pe
import os.path as op
from ephypype.interfaces.mne.LF_computation import LFComputation


data_path = mne.datasets.testing.data_path()
sbj_id = 'sample'
subjects_dir = op.join(data_path, 'subjects')
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


def test_LFComputation():
    """Test LF interface."""

    lf_node = pe.Node(interface=LFComputation(), name='LF')
    lf_node.inputs.sbj_id = 'sample'
    lf_node.inputs.subjects_dir = subjects_dir
    lf_node.inputs.raw_fname = raw_fname
    lf_node.inputs.spacing = 'oct-5'

    lf_node.run()

    assert lf_node.result.outputs.fwd_filename


def test_mixed_LFComputation():
    """Test LF interface."""

    lf_node = pe.Node(interface=LFComputation(), name='LF')
    lf_node.inputs.sbj_id = 'sample'
    lf_node.inputs.subjects_dir = subjects_dir
    lf_node.inputs.raw_fname = raw_fname
    lf_node.inputs.spacing = 'oct-5'
    lf_node.inputs.aseg = True
    lf_node.inputs.aseg_labels = ['Left-Amygdala']

    lf_node.run()

    assert lf_node.result.outputs.fwd_filename
