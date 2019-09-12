"""fif convertors."""

import os
import numpy as np
import mne
from mne.io import read_raw_fif
from nipype.utils.filemanip import split_filename as split_f
from .aux_tools import nostdout


def _ep2ts(fif_file):
    """Read fif file with epoched data and save timeseries to .npy."""
    from mne import read_epochs

    from numpy import save
    import os.path as op

    with nostdout():
        epochs = read_epochs(fif_file)

    epochs_meg = epochs.pick_types(meg=True, eeg=False, eog=False, ecg=False)

    data = epochs_meg.get_data()
    save_path = op.abspath('ts_epochs.npy')
    save(save_path, data)
    return save_path


def _get_raw_array(raw_fname, save_data=True):
    """Read a raw data from **.fif** file and save the data time series, the
    sensors coordinates and labels in .npy and .txt files.

    Parameters
    ----------
    raw_fname : str
        pathname of the raw data to read

    Returns
    -------
    array_file : str
        pathname of the numpy file (.npy) containing the data read from
        raw_fname
    channel_coords_file : str
        pathname of .txt file containing the channels coordinates
    channel_names_file : str
        pathname of .txt file containing the channels labels
    sfreq : float
        sampling frequency
    """
    raw = read_raw_fif(raw_fname, preload=True)
    subj_path, basename, ext = split_f(raw_fname)
    select_sensors = mne.pick_types(raw.info, meg=True, ref_meg=False,
                                    exclude='bads')

    # save electrode locations
    sens_loc = [raw.info['chs'][i]['loc'][:3] for i in select_sensors]
    sens_loc = np.array(sens_loc)

    channel_coords_file = os.path.abspath('correct_channel_coords.txt')
    np.savetxt(channel_coords_file, sens_loc, fmt=str("%s"))

    # save electrode names
    ch_names = np.array([raw.ch_names[pos] for pos in select_sensors],
                        dtype='str')

    channel_names_file = os.path.abspath('correct_channel_names.txt')
    np.savetxt(channel_names_file, ch_names, fmt=str('%s'))

    if save_data:
        data, times = raw[select_sensors, :]
        print((data.shape))

        array_file = os.path.abspath(basename + '.npy')
        np.save(array_file, data)
        print('\n *** TS FILE {} *** \n'.format(array_file))
    else:
        array_file = None
    print('*** raw.info[sfreq] = {}'.format(raw.info['sfreq']))

    return array_file, channel_coords_file, channel_names_file, raw.info['sfreq']  # noqa
