"""Test fif2ts."""

import mne
import pytest
import os
import numpy as np

from ephypype.fif2array import ep2ts
from numpy.testing import assert_equal, assert_array_almost_equal

data_path = mne.datasets.testing.data_path()
raw_fname = os.path.join(data_path, 'MEG', 'sample',
                         'sample_audvis_trunc_raw.fif')


@pytest.mark.usefixtures("change_wd")
def test_ep2ts():
    """Test data conversion."""
    # Read data from file:
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
    epo_fif_filepath = data_path + 'sample-epo.fif'
    epochs.save(epo_fif_filepath)

    # Call ep2ts in order to write the timeseries of epoched data in .npy
    epo_filepath = ep2ts(epo_fif_filepath)

    epo_ts = np.load(epo_filepath)

    assert_equal(epo_ts.shape, epochs.get_data().shape)
    assert_array_almost_equal(epo_ts, epochs.get_data())
