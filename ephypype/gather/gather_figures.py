"""Get pipeline figures."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import glob
import re
import os.path as op

from nipype.utils.filemanip import split_filename as split_f


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

                        data_path, basename, ext = split_f(fig)

                        caption = 'Subject: {} Session: {} Frequency band: {}'.format(sbj, ses, band)  # noqa
                        captions.append(caption + ' epoch:' +
                                        re.findall('\\d+', basename)[0])

    return conn_figures, captions


def get_psd_figures(workflow_path, workflow_name, subject_id, session_id):
    """
    Get PSD plot.

    Inputs
       workflow_path : str
           Path of connectivity workflow
       workflow_name : str
           Name of the connectivity workflow
       subject_id : list of str
           List of subjects id
       session_id : list of str
           List of sessions

    Outputs
        conn_figures : list of str
            List of path of circularity graphs
        captions : list of str
            List of captions

    """
    psd_pipeline = 'power_pipeline'
    psd_node = 'power'

    conn_figures = list()
    captions = list()

    subjects_folder = '_session_id_{ses}_subject_id_{sbj}'
    node_path = op.join(workflow_path, workflow_name, psd_pipeline,
                        subjects_folder, psd_node)

    for sbj in subject_id:
        for ses in session_id:
            fig_path = node_path.format(ses=ses, sbj=sbj)

            figure = glob.glob(op.join(fig_path, '*.png'))
            if figure:
                for fig in figure:
                    conn_figures.append(fig)

                    data_path, basename, ext = split_f(fig)

                    caption = 'PSD for Subject: {} Session: {} '.format(sbj, ses)  # noqa
                    captions.append(caption)

    return conn_figures, captions
