"""Get pipeline results and figures."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import glob
import os.path as op


def get_channel_files(workflow_path, workflow_name):
    """Get channel files.

    Parameters
    ----------
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflows

    Returns
    -------
        channels_files : list of str
            List of path of channel coordinates files
        channels_name_files : list of str
            List of path of channel names files
    """
    channels_fname = 'correct_channel_coords.txt'
    channels_name_fname = 'correct_channel_names.txt'

    node_path = op.join(workflow_path, workflow_name, '*', '*')

    channels_files = _get_list(node_path, channels_fname)
    channels_name_files = _get_list(node_path, channels_name_fname)

    return channels_files, channels_name_files


def get_results(workflow_path, workflow_name, pipeline=None):
    """Get results files.

    Parameters
    ----------
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       pipeline : str
           name of the pipeline (possible values: 'connectivity', 'inverse',
           'psd', 'ica')

    Returns
    -------
        matrices : list of str
            List of path of results
    """
    if pipeline == 'connectivity':
        result_file = '*.npy'
        label_file = None
        node_path = op.join(workflow_path, workflow_name, '*', '*', '*')

    elif pipeline == 'power':
        result_file = '*.npz'
        label_file = '*coords.txt'
        node_path = op.join(workflow_path, workflow_name, '*', '*', '*')

    elif pipeline == 'inverse':
        result_file = '*.npy'
        label_file = '*.pkl'
        node_path = op.join(workflow_path, workflow_name, '*', '*', '*')

    elif pipeline == 'ica':
        result_file = '*ica_solution.fif'
        label_file = '*ica.fif'
        node_path = op.join(workflow_path, workflow_name, '*', '*', '*')

    elif pipeline == 'tfr_morlet':
        result_file = '*-tfr.h5'
        label_file = None
        node_path = op.join(workflow_path, workflow_name, '*', '*')

    elif pipeline == 'compute_evoked':
        result_file = '*-ave.fif'
        label_file = None
        node_path = op.join(workflow_path, workflow_name, '*', '*', '*')

    results_files = _get_list(node_path, result_file)

    if label_file:
        labels_file = _get_list(node_path, label_file)
    else:
        labels_file = None

    return results_files, labels_file


def _get_list(node_path, result_file):

    file_path = op.join(node_path, result_file)
    results_files = glob.glob(file_path)

    return results_files

# TODO add get figs on connectivity (*.png) and psd wf
