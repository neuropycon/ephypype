"""Get pipeline figures."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import glob
import re
import os.path as op

from mne import Report
from nipype.utils.filemanip import split_filename as split_f


def get_connectivity_figures(wf_path, wf_name, subject_ids, freq_band_names,
                             session_ids, report_filename='report.html'):

    import matplotlib.pyplot as plt

    connectivity_node = 'ts_to_conmat'
    plot_spectral_node = 'plot_spectral'

    conn_figures = list()
    captions = list()

    sbj_folder_template = \
        '_freq_band_name_{band}_session_id_{ses}_subject_id_{sbj}'
    fig_path_template = op.join(wf_path, wf_name, connectivity_node,
                                sbj_folder_template, plot_spectral_node)

    for sbj in subject_ids:
        for ses in session_ids:
            for band in freq_band_names:
                fig_path = fig_path_template.format(band=band, ses=ses,
                                                    sbj=sbj)

                figures = glob.glob(op.join(fig_path, '*.eps'))
                if figures:
                    for fig in figures:
                        f, ax = plt.subplots()
                        img = plt.imread(fig)
                        ax.figure.set_size_inches(8, 8)
                        ax.imshow(img)
                        conn_figures.append(f)

                        data_path, basename, ext = split_f(fig)
                        print(basename)

                        caption = 'Subject: {} Session: {} Frequency band: {}'.format(sbj, ses, band)  # noqa
                        captions.append(caption + ' epoch:' +
                                        re.findall('\d+', basename)[0])

    report = Report()
    report.add_figs_to_section(conn_figures, captions)

    report.save(report_filename, open_browser=False, overwrite=True)
