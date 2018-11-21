"""Get pipeline figures."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import glob
import re
import os.path as op

from nipype.utils.filemanip import split_filename as split_f


def get_connectivity_figures(wf_path, wf_name, subject_id, freq_band_names,
                             session_id, report_filename='report.html'):

    connectivity_node = 'ts_to_conmat'
    plot_spectral_node = 'plot_spectral'

    conn_figures = list()
    captions = list()

    subjects_folder = \
        '_freq_band_name_{band}_session_id_{ses}_subject_id_{sbj}'
    fig_path_template = op.join(wf_path, wf_name, connectivity_node,
                                subjects_folder, plot_spectral_node)

    for sbj in subject_id:
        for ses in session_id:
            for band in freq_band_names:
                fig_path = fig_path_template.format(band=band, ses=ses,
                                                    sbj=sbj)

                figures = glob.glob(op.join(fig_path, '*.png'))
                if figures:
                    for fig in figures:
                        conn_figures.append(fig)

                        data_path, basename, ext = split_f(fig)
                        print(basename)

                        caption = 'Subject: {} Session: {} Frequency band: {}'.format(sbj, ses, band)  # noqa
                        captions.append(caption + ' epoch:' +
                                        re.findall('\\d+', basename)[0])

    return conn_figures, captions
