"""Power functions."""

# Author: Dmitrii Altukhov <dm-altukhov@ya.ru>
#         Annalisa Pascarella <a.pascarella@iac.cnr.it>
import os
import numpy as np

from nipype.utils.filemanip import split_filename
from mne import read_epochs
from mne.io import read_raw_fif
from scipy.signal import welch

from .fif2array import _get_raw_array


def _compute_and_save_psd(data_fname, fmin=0, fmax=120,
                          method='welch', is_epoched=False,
                          n_fft=256, n_overlap=0,
                          picks=None, proj=False, n_jobs=1, verbose=None):
    """Load epochs/raw from file, compute psd and save the result."""

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

    _get_raw_array(data_fname, save_data=False)

    psds_fname = _save_psd(data_fname, psds, freqs)
    _save_psd_img(data_fname, psds, freqs, is_epoched, method)

    return psds_fname


def _compute_and_save_src_psd(data_fname, sfreq, fmin=0, fmax=120,
                              is_epoched=False,
                              n_fft=256, n_overlap=0,
                              n_jobs=1, verbose=None):
    """Load epochs/raw from file, compute psd and save the result."""
    src_data = np.load(data_fname)
    dim = src_data.shape
    if len(dim) == 3 and dim[0] == 1:
        src_data = np.squeeze(src_data)
    print(('src data dim: {}'.format(src_data.shape)))

    if n_fft > src_data.shape[1]:
        nperseg = src_data.shape[1]
    else:
        nperseg = n_fft

    n_freqs = nperseg // 2 + 1
    psds = np.empty([src_data.shape[0], n_freqs])
    for i in range(src_data.shape[0]):
        freqs, Pxx = welch(src_data[i, :], fs=sfreq, window='hamming',
                           nperseg=nperseg, noverlap=n_overlap, nfft=None)
        psds[i, :] = Pxx

    psds_fname = _save_psd(data_fname, psds, freqs)
    _save_psd_img(data_fname, psds, freqs, is_epoched)

    return psds_fname


def _compute_mean_band_psd(psds_file, freq_bands):
    """Compute mean band psd."""
    npzfile = np.load(psds_file)
    print(('the .npz file contain {} \n'.format(npzfile.files)))

    # is a matrix with dim n_channels(n_voxel) x n_freqs
    psds = npzfile['psds']
    print(('psds is a matrix {} \n'.format(psds.shape)))

    # list of frequencies in which psds was computed;
    # its length = columns of psds
    freqs = npzfile['freqs']
    print(('freqs contains {} frequencies \n'.format(len(freqs))))

    n_row, _ = psds.shape
    n_fr = len(freq_bands)

    m_px = np.empty([n_row, n_fr])

    for f in range(n_fr):
        min_fr = freq_bands[f][0]
        max_fr = freq_bands[f][1]
        print(('*** frequency band [{}, {}] ***\n'.format(min_fr, max_fr)))
        m_px[:, f] = np.mean(psds[:, (freqs >= min_fr) * (freqs <= max_fr)], 1)

    psds_mean_fname = _save_m_px(psds_file, m_px)

    return psds_mean_fname


def _save_m_px(psds_file, m_px):
    data_path, basename, ext = split_filename(psds_file)

    psds_mean_fname = basename + '-mean_band.npy'
    psds_mean_fname = os.path.abspath(psds_mean_fname)
    print((m_px.shape))
    np.save(psds_mean_fname, m_px)

    return psds_mean_fname


def _save_psd(data_fname, psds, freqs):
    data_path, basename, ext = split_filename(data_fname)

    psds_fname = basename + '-psds.npz'
    psds_fname = os.path.abspath(psds_fname)
    print((psds.shape))
    print(('*** save {} ***'.format(psds_fname)))
    np.savez(psds_fname, psds=psds, freqs=freqs)

    return psds_fname


def _save_psd_img(data_fname, psds, freqs, is_epoched=False, method=''):
    import matplotlib.pyplot as plt

    data_path, basename, ext = split_filename(data_fname)
    psds_img_fname = basename + '-psds.png'
    psds_img_fname = os.path.abspath(psds_img_fname)

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

    print(('*** save {} ***'.format(psds_img_fname)))
    plt.savefig(psds_img_fname)
