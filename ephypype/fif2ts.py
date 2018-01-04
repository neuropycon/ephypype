""" fif convertors """

from ephypype.aux_tools import nostdout


def ep2ts(fif_file):
    """Read fif file with raw data or epochs and save
    timeseries to .npy
    """
    from mne import read_epochs
    from mne import pick_types

    from numpy import save
    import os.path as op

    with nostdout():
        epochs = read_epochs(fif_file)

    epochs_meg = epochs.pick_types(meg=True, eeg=False, eog=False, ecg=False)

    data = epochs_meg.get_data()
    save_path = op.abspath('ts_epochs.npy')
    save(save_path, data)
    return save_path
