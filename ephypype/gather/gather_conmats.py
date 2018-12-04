"""Gather conmats."""
import re

import numpy as np
import itertools as iter
from itertools import combinations

from mne.viz import circular_layout, plot_connectivity_circle


def _atoi(text):
    """Get digit."""
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """alist.sort(key=natural_keys) sorts in human order.

    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """

    return [_atoi(c) for c in re.split(r'(\d+)', str(text))]


def return_full_mat(mat, elec_labels, all_elec_labels):
    """Get full mat."""
    n_labs = len(elec_labels)
    assert len(mat.shape) == 2 and mat.shape[0] == mat.shape[1], (
        "Error mat shape = {} should be a 2D squared ndarray "
        "(matrix)".format(mat.shape))
    assert n_labs == mat.shape[0] and n_labs == mat.shape[1], (
        "Error, both mat dimension {} {} should be the same as "
        "elec_labels {}".format(mat.shape[0], mat.shape[1],
                                len(elec_labels)))

    # if undirected (values are not the same on both triangular parts)
    if np.sum(mat[np.tril_indices(mat.shape[0], k=-1)]) != np.sum(mat[
            np.triu_indices(mat.shape[0], k=1)]):
        mat = mat + np.transpose(mat)

    # building full_mat from all_elec_labels

    full_mat = np.empty((len(all_elec_labels), len(all_elec_labels)))
    full_mat[:] = np.NAN

    for pair_lab in iter.permutations(all_elec_labels, 2):

        all_i, all_j = all_elec_labels.index(
            pair_lab[0]), all_elec_labels.index(pair_lab[1])

        if pair_lab[0] in elec_labels and pair_lab[1] in elec_labels:

            i, j = elec_labels.index(
                pair_lab[0]), elec_labels.index(pair_lab[1])

            full_mat[all_i, all_j] = mat[i, j]

    return full_mat


def plot_tab_circular_connectivity(list_list_conmat, all_elec_labels,
                                   plot_filename, coh_low_thresh=0.0,
                                   coh_high_thresh=1.0,
                                   color_bar='gist_rainbow', column_labels=[],
                                   row_labels=[]):
    """Plot tab circular conectivity."""
    import matplotlib.pyplot as plt
    nb_lines = len(list_list_conmat)
    print(nb_lines)

    print(len(list_list_conmat[0]))

    if len(list_list_conmat) != 1:
        for i, j in combinations(list(range(nb_lines)), 2):
            assert len(list_list_conmat[i]) == len(list_list_conmat[j]), (
                "Error, not all the same length {} != "
                "{}".format(len(list_list_conmat[i]),
                            len(list_list_conmat[j])))

    nb_cols = len(list_list_conmat[0])

    # for i in
    # print list_list_conmat[0][0].shape

    # Angles
    bounds = [0, len(all_elec_labels) / 2]
    all_node_angles = circular_layout(all_elec_labels,
                                      node_order=all_elec_labels, start_pos=90,
                                      group_boundaries=bounds)

    # print all_node_angles

    fig, axes = plt.subplots(nrows=nb_lines, ncols=nb_cols,
                             figsize=(4 * nb_cols, 4 * nb_lines),
                             facecolor='black')
    # fig = plt.figure(num=None, figsize=(4*nb_cols, 4*nb_lines),
    # facecolor='black')

    if len(column_labels) == 0:
        column_labels = ['Column {}'.format(col) for col in range(nb_cols)]

    if len(row_labels) == 0:
        row_labels = ['Line {}'.format(row) for row in range(nb_lines)]

    assert len(column_labels) == nb_cols, (
        "Error, specifying invalid number of column labels")
    assert len(row_labels) == nb_lines, (
        "Error, specifying invalid number of line labels")

    for index_sess, list_conmat in enumerate(list_list_conmat):

        print(len(list_conmat))

        for index_win, np_all_mean_con_mats in enumerate(list_conmat):

            print(np_all_mean_con_mats.shape)

            kw = dict(textcolor="black", facecolor="white", n_lines=None,
                      node_angles=all_node_angles, fontsize_names=15,
                      show=False, colormap=color_bar, vmin=coh_low_thresh,
                      vmax=coh_high_thresh, fig=fig,
                      subplot=(nb_lines,
                               nb_cols, 1 + index_win + nb_cols * index_sess))
            if index_win == len(list_conmat) - 1:
                fig, ax = plot_connectivity_circle(np_all_mean_con_mats,
                                                   all_elec_labels,
                                                   colorbar_size=0.5, **kw)
                # (nb_lines,nb_cols,1+index_win+nb_cols*index_sess))

            else:
                fig, ax = plot_connectivity_circle(np_all_mean_con_mats,
                                                   all_elec_labels,
                                                   colorbar=False, **kw)

            if index_win == 0:
                ax.set_ylabel(row_labels[index_sess],
                              rotation=0, size='large', fontsize=25)

            if index_sess == 0:
                ax.set_title(column_labels[index_win],
                             fontdict={'fontsize': 25})

    # saving
    print(plot_filename)

    fig.savefig(plot_filename, facecolor='white')

    plt.close(fig)
    # fig1.close()
    del fig
