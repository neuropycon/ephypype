# Author: David Meunier <david_meunier_79@hotmail.fr>


# ------------------- compute spectral connectivity ------------------------- #
def compute_spectral_connectivity(data, con_method, sfreq, fmin, fmax,
                                  mode='cwt_morlet'):

    print('MODE is {}'.format(mode))
    import numpy as np
    from mne.connectivity import spectral_connectivity

    if len(data.shape) < 3:
        if con_method in ['coh', 'cohy', 'imcoh']:
            data = data.reshape(1, data.shape[0], data.shape[1])

        elif con_method in ['pli', 'plv', 'ppc', 'pli',
                            'pli2_unbiased', 'wpli', 'wpli2_debiased']:
            print("warning, only work with epoched time series")
            sys.exit()

    if mode == 'multitaper':

        con_matrix, _, _, _, _ = spectral_connectivity(
            data, method=con_method, sfreq=sfreq, fmin=fmin,
            fmax=fmax, faverage=True, tmin=None, mode='multitaper',
            mt_adaptive=False, n_jobs=1)

        print((con_matrix.shape))

        con_matrix = np.array(con_matrix[:, :, 0])

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
        print('Time-frequency transformation mode is not set')
        return None

    print(con_matrix.shape)
    print(np.min(con_matrix), np.max(con_matrix))

    return con_matrix


# ----------------------- compute and save  ----------------------- #
def compute_and_save_spectral_connectivity(data, con_method, sfreq, fmin, fmax,
                                           index=0, mode='cwt_morlet',
                                           export_to_matlab=False):

    import os

    import numpy as np
    from scipy.io import savemat

    print(data.shape)

    # from ephypype.spectral import compute_spectral_connectivity

    con_matrix = compute_spectral_connectivity(
        data, con_method, sfreq, fmin, fmax, mode)

    conmat_file = os.path.abspath(
        "conmat_" + str(index) + "_" + con_method + ".npy")

    np.save(conmat_file, con_matrix)

    if export_to_matlab:

        conmat_matfile = os.path.abspath(
            "conmat_" + str(index) + "_" + con_method + ".mat")

        savemat(conmat_matfile, {
            "conmat": con_matrix + np.transpose(con_matrix)})

    return conmat_file


def compute_and_save_multi_spectral_connectivity(all_data, con_method, sfreq,
                                                 fmin, fmax, mode='cwt_morlet',
                                                 export_to_matlab=False):

    from ephypype.spectral import compute_and_save_spectral_connectivity

    print((all_data.shape))

    if len(all_data.shape) != 3:

        print("Warning, all_data should have several samples")

        return []

    conmat_files = []

    for i in range(all_data.shape[0]):

        cur_data = all_data[i, :, :]

        print((cur_data.shape))

        data = cur_data.reshape(1, cur_data.shape[0], cur_data.shape[1])

        print((data.shape))

        conmat_file = compute_and_save_spectral_connectivity(
            data, con_method, sfreq, fmin, fmax, index=i,
            mode=mode, export_to_matlab=export_to_matlab)

        conmat_files.append(conmat_file)

    return conmat_files


# -------------------- plot spectral connectivity -------------------- #
def plot_circular_connectivity(conmat, label_names, node_colors, node_order,
                               vmin=0.3, vmax=1.0, nb_lines=200, fname="_def"):
    """Plot circular connectivity"""

    import os
    import numpy as np
    from mne.viz import circular_layout, plot_connectivity_circle
    import matplotlib.pyplot as plt

    # Angles
    node_angles = circular_layout(label_names, node_order, start_pos=90,
                                  group_boundaries=[0, len(label_names) / 2])
    print(conmat)
    print((node_angles.astype(int)))

    conmat = conmat + np.transpose(conmat)

    # Plot the graph using node colors from the FreeSurfer parcellation.
    # We only show the 300 strongest connections.
    fig, _ = plot_connectivity_circle(conmat,
                                      label_names,
                                      n_lines=nb_lines,
                                      node_angles=node_angles.astype(int),
                                      node_colors=None,
                                      fontsize_names=12,
                                      title='All-to-All Connectivity',
                                      show=False,
                                      vmin=vmin,
                                      vmax=vmax)

    # plt.show()
    # print fig
    # plot_conmat_file = os.path.abspath('circle.png')
    plot_conmat_file = os.path.abspath('circle_' + fname + '.eps')
    fig.savefig(plot_conmat_file, facecolor='black')
    # fig.savefig(plot_conmat_file)

    plt.close(fig)
    # fig1.close()
    del fig

    return plot_conmat_file


def filter_adj_plot_mat(conmat_file, labels_file, sep_label_name, k_neigh):
    """Filter adjacency matrix"""

    import numpy as np
    import os

    from itertools import combinations

    labels = [line.strip().split(sep_label_name) for line in open(labels_file)]

    print(labels)

    triu_indices = np.triu_indices(len(labels), 1)

    print(triu_indices)

    adj_mat = np.zeros(shape=(len(labels), len(labels)), dtype=bool)

    for i in range(k_neigh):

        adj_plots = [(a[0] == b[0]) and ((int(a[1]) + i + 1) == int(b[1]))
                     for a, b in combinations(labels, 2)]

        print((len(adj_plots)))

        adj_mat[triu_indices] = adj_mat[triu_indices] + adj_plots

        print(np.sum(adj_mat))

    print(adj_mat)

    # loading ad filtering conmat_file
    conmat = np.load(conmat_file)

    print(conmat)

    assert conmat.shape[0] == len(
        labels), "warning, wrong dimensions between labels and conmat"

    filtered_conmat = np.transpose(conmat).copy()

    # print np.transpose(adj_mat) == True

    xx, yy = np.where(adj_mat)

    filtered_conmat[xx, yy] = 0.0

    print(filtered_conmat)

    filtered_conmat_file = os.path.abspath("filtered_conmat.npy")

    np.save(filtered_conmat_file, np.transpose(filtered_conmat))

    return filtered_conmat_file
