"""Spectral functions."""

# Author: David Meunier <david_meunier_79@hotmail.fr>
#
# License: BSD (3-clause)

import os
import numpy as np

from scipy.io import savemat

from nipype.utils.filemanip import split_filename

from mne import read_epochs
from mne.connectivity import spectral_connectivity
from mne.viz import circular_layout, plot_connectivity_circle
from mne.time_frequency import tfr_morlet, write_tfrs


def _compute_spectral_connectivity(data, con_method, sfreq, fmin, fmax,
                                   mode='cwt_morlet', gathering_method="mean"):
    """compute spectral connectivity"""
    print('MODE is {}'.format(mode))

    if len(data.shape) < 3:
        if con_method in ['coh', 'cohy', 'imcoh']:
            data = data.reshape(1, data.shape[0], data.shape[1])

        elif con_method in ['pli', 'plv', 'ppc', 'pli',
                            'pli2_unbiased', 'wpli', 'wpli2_debiased']:
            raise ValueError("{} only work with epoched time series".format(
                             con_method))

    if mode == 'multitaper':
        if gathering_method == "mean":
            con_matrix, _, _, _, _ = spectral_connectivity(
                data, method=con_method, sfreq=sfreq, fmin=fmin,
                fmax=fmax, faverage=True, tmin=None, mode='multitaper',
                mt_adaptive=False, n_jobs=1)

            con_matrix = np.array(con_matrix[:, :, 0])

        elif gathering_method == "max":
            con_matrix, _, _, _, _ = spectral_connectivity(
                data, method=con_method, sfreq=sfreq, fmin=fmin,
                fmax=fmax, faverage=False, tmin=None, mode='multitaper',
                mt_adaptive=False, n_jobs=1)

            con_matrix = np.amax(con_matrix, axis=2)

        elif gathering_method == "none":

            con_matrix, _, _, _, _ = spectral_connectivity(
                data, method=con_method, sfreq=sfreq, fmin=fmin,
                fmax=fmax, faverage=False, tmin=None, mode='multitaper',
                mt_adaptive=False, n_jobs=1)

        else:
            raise ValueError('Unknown gathering method')

    elif mode == 'cwt_morlet':

        frequencies = np.arange(fmin, fmax, 1)
        n_cycles = frequencies / 7.

        print(data)

        con_matrix, _, _, _, _ = spectral_connectivity(
            data, method=con_method, sfreq=sfreq, faverage=True,
            tmin=None, mode='cwt_morlet', cwt_frequencies=frequencies,
            cwt_n_cycles=n_cycles, n_jobs=1)

        con_matrix = np.mean(np.array(con_matrix[:, :, 0, :]), axis=2)
    else:
        raise ValueError('Time-frequency transformation mode is not set')

    print(con_matrix.shape)
    print(np.min(con_matrix), np.max(con_matrix))

    return con_matrix


def _compute_and_save_spectral_connectivity(data, con_method, sfreq, fmin, fmax,  # noqa
                                            index=0, mode='cwt_morlet',
                                            export_to_matlab=False,
                                            gathering_method="mean",
                                            save_dir=None):
    """Compute and save spectral connectivity."""
    con_matrix = _compute_spectral_connectivity(data, con_method, sfreq, fmin,
                                                fmax, mode, gathering_method)

    if save_dir is not None:
        conmat_file = os.path.join(save_dir, "conmat_{}_{}.npy".format(
            index, con_method))
    else:
        conmat_file = os.path.abspath("conmat_{}_{}.npy".format(
            index, con_method))

    np.save(conmat_file, con_matrix)

    if export_to_matlab:

        if save_dir is not None:
            conmat_matfile = os.path.join(
                save_dir, "conmat_{}_{}.mat".format(index, con_method))
        else:
            conmat_matfile = os.path.abspath(
                "conmat_{}_{}.mat".format(index, con_method))

        savemat(conmat_matfile, {
            "conmat": con_matrix + np.transpose(con_matrix)})

    return conmat_file


def _compute_and_save_multi_spectral_connectivity(all_data, con_method, sfreq,
                                                  fmin, fmax, mode='cwt_morlet',  # noqa
                                                  export_to_matlab=False,
                                                  gathering_method="mean",
                                                  save_dir=None):
    """Compute and save multi-spectral connectivity."""
    assert len(all_data.shape) == 3, ("Error, \
        all_data should have several samples")

    conmat_files = []

    for i in range(all_data.shape[0]):

        cur_data = all_data[i, :, :]

        print((cur_data.shape))

        data = cur_data.reshape(1, cur_data.shape[0], cur_data.shape[1])

        print((data.shape))

        conmat_file = _compute_and_save_spectral_connectivity(
            data, con_method, sfreq, fmin, fmax, index=i,
            mode=mode, export_to_matlab=export_to_matlab,
            gathering_method=gathering_method, save_dir=save_dir)

        conmat_files.append(conmat_file)

    return conmat_files


def _plot_circular_connectivity(conmat, label_names, node_colors=None,
                                node_order=[], vmin=0.3, vmax=1.0,
                                nb_lines=200, fname="_def", save_dir=None):
    """Plot circular connectivity."""
    import matplotlib.pyplot as plt

    assert len(conmat.shape) == 2, "Error, conmat should be 2D matrix"
    assert conmat.shape[0] == conmat.shape[1], "Error, conmat should squared"
    assert conmat.shape[0] == len(label_names), "Error, conmat and labels\
        should have same length {} != {}".format(
        conmat.shape[0], len(label_names))

    # if not defined, use label_names
    if len(node_order) == 0:
        node_order = label_names

    # Angles
    node_angles = circular_layout(label_names, node_order, start_pos=90,
                                  group_boundaries=[0, len(label_names) / 2])

    # necessary to have symetric matrix
    conmat = conmat + np.transpose(conmat)

    # Plot the graph
    fig, _ = plot_connectivity_circle(conmat, label_names, n_lines=nb_lines,
                                      node_angles=node_angles.astype(int),
                                      node_colors=None, fontsize_names=12,
                                      title='All-to-All Connectivity',
                                      show=False, vmin=vmin, vmax=vmax)

    # saving circle file
    if save_dir is not None:
        assert os.path.exists(save_dir), ("Error, do not use save_dir if it \
            does not exists before")
        plot_conmat_file = os.path.join(save_dir, 'circle_' + fname + '.png')
    else:
        plot_conmat_file = os.path.abspath('circle_' + fname + '.png')

    fig.savefig(plot_conmat_file, facecolor='black')
    plt.close(fig)
    return plot_conmat_file


def _compute_tfr_morlet(epo_fpath, freqs, n_cycles):

    assert os.path.exists(epo_fpath)

    epochs = read_epochs(epo_fpath)

    power = tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles,
                       use_fft=True, return_itc=False, decim=3, n_jobs=1)

    data_path, basename, ext = split_filename(epo_fpath)

    tfr_fname = os.path.abspath(basename + '-tfr.h5')
    print((power.data.shape))
    print(('*** save {} ***'.format(tfr_fname)))
    write_tfrs(tfr_fname, power, overwrite=True)

    return tfr_fname
