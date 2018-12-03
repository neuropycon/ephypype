"""Test power."""
import mne
import pytest
import os.path as op
import numpy as np
import nipype.pipeline.engine as pe
from ephypype.interfaces.mne.power import Power
from ephypype.nodes.power_tools import PowerBand


import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')


@pytest.mark.usefixtures("change_wd")
def test_power_welch():
    """Test computing and saving PSD."""
    fmin = 0.1
    fmax = 40

    power_node = pe.Node(interface=Power(), name='welch_psd')

    power_node.inputs.data_file = raw_fname
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.method = 'welch'

    power_node.run()

    psd_file = power_node.result.outputs.psds_file
    power = np.load(psd_file)

    raw = mne.io.read_raw_fif(raw_fname)
    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == power['psds'].shape[0]
    assert len(power['freqs']) == power['psds'].shape[1]


def test_power_multitaper():
    """Test computing and saving PSD."""
    fmin = 0.1
    fmax = 40

    power_node = pe.Node(interface=Power(), name='multitaper_psd')

    power_node.inputs.data_file = raw_fname
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.method = 'multitaper'

    power_node.run()

    psd_file = power_node.result.outputs.psds_file
    power = np.load(psd_file)

    raw = mne.io.read_raw_fif(raw_fname)
    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == power['psds'].shape[0]
    assert len(power['freqs']) == power['psds'].shape[1]


def test_power_band():
    """Test computing mean PSD on specified band."""
    fmin = 0.1
    fmax = 40
    band = [[8, 12], [13, 29]]

    power_node = pe.Node(interface=Power(), name='welch_psd')

    power_node.inputs.data_file = raw_fname
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.method = 'welch'

    power_node.run()

    power_band_node = pe.Node(interface=PowerBand(), name='power_band')
    power_band_node.inputs.psds_file = power_node.result.outputs.psds_file
    power_band_node.inputs.freq_bands = band

    power_band_node.run()

    mean_psd = np.load(power_band_node.result.outputs.mean_power_band_file)
    raw = mne.io.read_raw_fif(raw_fname)
    picks = mne.pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

    assert len(picks) == mean_psd.shape[0]
    assert len(band) == mean_psd.shape[1]
