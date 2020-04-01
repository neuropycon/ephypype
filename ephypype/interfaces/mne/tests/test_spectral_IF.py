"""Test preproc."""

import mne
import pytest
import os.path as op
import numpy as np

import nipype.pipeline.engine as pe

from ephypype.interfaces.mne.spectral import TFRmorlet

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server

data_path = mne.datasets.testing.data_path()
raw_fname = op.join(data_path, 'MEG', 'sample',
                    'sample_audvis_trunc_raw.fif')
events_file = op.join(data_path, 'MEG', 'sample',
                      'sample_audvis_trunc_raw-eve.fif')


@pytest.mark.usefixtures("change_wd")
def test_tfr():
    """Test time-frequency transform (PSD and ITC)."""

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
    epochs.save(epo_fname, overwrite=True)

    # Test
    freqs = np.arange(6, 20, 5)
    compute_tfr_morlet = pe.Node(interface=TFRmorlet(), name='tfr_morlet')
    compute_tfr_morlet.inputs.freqs = freqs
    compute_tfr_morlet.inputs.n_cycles = freqs / 4.
    compute_tfr_morlet.inputs.epo_file = epo_fname

    compute_tfr_morlet.run()

    assert compute_tfr_morlet.result.outputs.power_file
