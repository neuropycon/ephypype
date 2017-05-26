"""Power functions"""
# Author: Dmitrii Altukhov <dm-altukhov@ya.ru>


def compute_and_save_psd(data_fname, fmin=0, fmax=120,
                         method='welch', is_epoched=False,
                         n_fft=256, n_overlap=0,
                         picks=None, proj=False, n_jobs=1, verbose=None):
    """
    Load epochs/raw from file,
    compute psd and save the result in numpy arrays
    """
    import os
    import matplotlib.pyplot as plt
    import numpy as np

    from mne import read_epochs
    from mne.io import read_raw_fif

    if is_epoched:
        epochs = read_epochs(data_fname)
    else:
        epochs = read_raw_fif(data_fname, preload=True)

    epochs_meg = epochs.pick_types(meg=True, eeg=False, eog=False, ecg=False)

    if method == 'welch':
        from mne.time_frequency import psd_welch
        psds, freqs = psd_welch(epochs_meg, fmin=fmin, fmax=fmax)
    elif method == 'multitaper':
        from mne.time_frequency import psd_multitaper
        psds, freqs = psd_multitaper(epochs_meg, fmin=fmin, fmax=fmax)
    else:
        raise Exception('nonexistent method for psd computation')
    path, name = os.path.split(data_fname)
    base, ext = os.path.splitext(name)
    psds_fname = base + '-psds.npz'
    # freqs_fname = base + '-freqs.npy'
    psds_fname = os.path.abspath(psds_fname)
    # print(psds.shape)
    np.savez(psds_fname, psds=psds, freqs=freqs)
    # np.save(freqs_file, freqs)

    # save PSD as img
    f, ax = plt.subplots()
    psds = 10 * np.log10(psds)
    if is_epoched:
        psds_mean = psds.mean(0).mean(0)
        psds_std = psds.mean(0).std(0)
    else:
        psds_mean = psds.mean(0)
        psds_std = psds.std(0)

    ax.plot(freqs, psds_mean, color='g')
    ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
                    color='g', alpha=.5)
    ax.set(title='{} PSD'.format(method), xlabel='Frequency',
           ylabel='Power Spectral Density (dB)')

    psds_img_fname = base + '-psds.png'
    psds_img_fname = os.path.abspath(psds_img_fname)
    plt.savefig(psds_img_fname)

    return psds_fname
