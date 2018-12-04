"""Get pipeline results and figures."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import glob
import re
import os.path as op
from nipype.utils.filemanip import split_filename


def get_connectivity_matrices(workflow_path, workflow_name, subject_id,
                              session_id, freq_band_names, is_channel=False):
    """
    Get connectivity matrices.

    Inputs
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions
       freq_band_names : list of str
           The frequency band names

    Outputs
        conn_matrices : list of str
            List of path of connecivity matrix
        channel_coo_files : list of str
            List of path of channel coordinates files
    """
    connectivity_pipeline = 'ts_to_conmat'
    spectral_node = 'spectral'

    conn_matrices = list()
    channel_coo_files = list()
    channel_name_files = list()

    subjects_folder = \
        '_freq_band_name_{band}_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, connectivity_pipeline,
                        subjects_folder, spectral_node)

    for sbj in subject_id:
        for ses in session_id:
            for band in freq_band_names:
                file_path = node_path.format(band=band, ses=ses,
                                             sbj=sbj)

                conn_matrix = glob.glob(op.join(file_path, '*.npy'))
                if conn_matrix:
                    conn_matrices.append(conn_matrix[0])

                if is_channel:
                    fif2array_node = 'Fif2Array'
                    channel_coo_fname = 'correct_channel_coords.txt'
                    channel_name_fname = 'correct_channel_names.txt'
                    channel_file = op.join(workflow_path, workflow_name,
                                           subjects_folder.format(band=band,
                                                                  ses=ses,
                                                                  sbj=sbj),
                                           fif2array_node, channel_coo_fname)
                    channel_coo_files.append(channel_file)

                    channel_file = op.join(workflow_path, workflow_name,
                                           subjects_folder.format(band=band,
                                                                  ses=ses,
                                                                  sbj=sbj),
                                           fif2array_node, channel_name_fname)
                    channel_name_files.append(channel_file)

    return conn_matrices, channel_coo_files, channel_name_files


def get_connectivity_figures(workflow_path, workflow_name, subject_id,
                             session_id, freq_band_names):
    """
    Get circular graphs of connectivity matrices.

    Inputs
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions
       freq_band_names : list of str
           The frequency band names

    Outputs
        conn_figures : list of str
            List of path of circularity graphs
        captions : list of str
            List of captions

    """
    connectivity_pipeline = 'ts_to_conmat'
    plot_spectral_node = 'plot_spectral'

    conn_figures = list()
    captions = list()

    subjects_folder = \
        '_freq_band_name_{band}_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, connectivity_pipeline,
                        subjects_folder, plot_spectral_node)

    for sbj in subject_id:
        for ses in session_id:
            for band in freq_band_names:
                fig_path = node_path.format(band=band, ses=ses,
                                            sbj=sbj)

                figures = glob.glob(op.join(fig_path, '*.png'))
                if figures:
                    for fig in figures:
                        conn_figures.append(fig)

                        data_path, basename, ext = split_filename(fig)

                        caption = 'Subject: {} Session: {} Frequency band: {}'.format(sbj, ses, band)  # noqa
                        captions.append(caption + ' epoch:' +
                                        re.findall('\\d+', basename)[0])

    return conn_figures, captions


def get_psd_files(workflow_path, workflow_name, subject_id, session_id):
    """
    Get PSD file.

    Parameters
    ----------
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions

    Returns
    -------
        psd_file : list of str
            List of path of psd files
        channel_coo_files : list of str
            List of path of channel coordinates files
    """
    psd_pipeline = 'power_pipeline'
    psd_node = 'power'

    psd_files = list()
    channel_coo_files = list()

    subjects_folder = '_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, psd_pipeline,
                        subjects_folder, psd_node)

    for sbj in subject_id:
        for ses in session_id:
            file_path = node_path.format(ses=ses, sbj=sbj)
            psd_file = glob.glob(op.join(file_path, '*.npz'))
            coo_file = glob.glob(op.join(file_path, '*coords.txt'))
            if psd_file:
                psd_files.append(psd_file[0])
            if coo_file:
                channel_coo_files.append(coo_file[0])

    return psd_files, channel_coo_files


def get_inverse_files(workflow_path, workflow_name, subject_id, session_id):
    """
    Get source reconstruction files.

    Parameters
    ----------
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions

    Returns
    -------
        time_series_file : list of str
            List of path of source reconstruction files
        label_files : list of str
            List of path of labels pickle file
    """
    inverse_pipeline = 'inv_sol_pipeline'
    inverse_node = 'inv_solution'

    time_series_files = list()
    label_files = list()

    subjects_folder = '_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, inverse_pipeline,
                        subjects_folder, inverse_node)

    for sbj in subject_id:
        for ses in session_id:
            file_path = node_path.format(ses=ses, sbj=sbj)
            inverse_file = glob.glob(op.join(file_path, '*.npy'))
            label_file = glob.glob(op.join(file_path, '*.pkl'))
            if inverse_file:
                time_series_files.append(inverse_file[0])
            if label_file:
                label_files.append(label_file[0])

    return time_series_files, label_files


def get_ica_solution(workflow_path, workflow_name, subject_id, session_id):
    """
    Get ica solution.

    Parameters
    ----------
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions

    Returns
    -------
        ica_solution_file : list of str
            List of path of source reconstruction files
        label_files : list of str
            List of path of labels pickle file
    """
    ica_pipeline = 'preproc_meeg_pipeline'
    ica_node = 'ica'

    ica_files = list()
    raw_files = list()

    subjects_folder = '_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, ica_pipeline,
                        subjects_folder, ica_node)

    for sbj in subject_id:
        for ses in session_id:
            file_path = node_path.format(ses=ses, sbj=sbj)
            ica_file = glob.glob(op.join(file_path, '*ica_solution.fif'))
            raw_file = glob.glob(op.join(file_path, '*ica.fif'))
            if ica_file:
                ica_files.append(ica_file[0])
            if raw_file:
                raw_files.append(raw_file[0])

    return ica_files, raw_files
