"""Source estimate functions."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import mne
import numpy as np
import os.path as op

from mne import get_volume_labels_from_src

from .import_data import write_hdf5
from .source_space import _create_MNI_label_files


def _process_stc(stc, basename, sbj_id, subjects_dir, parc, forward,
                 aseg, is_fixed, all_src_space=False, ROIs_mean=True):
    if not isinstance(stc, list):
        print('***')
        print(('stc dim ' + str(stc.shape)))
        print('***')

        stc = [stc]
    else:
        print('***')
        print(('len stc %d' % len(stc)))
        print('***')

    print('**************************************************************')
    print('all_src_space: {}'.format(all_src_space))
    print('ROIs_mean: {}'.format(ROIs_mean))
    print('**************************************************************')
    if all_src_space:
        stc_data = list()
        stc_file = op.abspath(basename + '_stc.hdf5')

        for i in range(len(stc)):
            stc_data.append(stc[i].data)

        write_hdf5(stc_file, stc_data, dataset_name='stc_data')

    if ROIs_mean:
        label_ts, labels_file, label_names_file, label_coords_file = \
            _compute_mean_ROIs(stc, sbj_id, subjects_dir, parc,
                               forward, aseg, is_fixed)

        ts_file = op.abspath(basename + '_ROI_ts.npy')
        np.save(ts_file, label_ts)

    else:
        ts_file = stc_file
        labels_file = ''
        label_names_file = ''
        label_coords_file = ''

    return ts_file, labels_file, label_names_file, label_coords_file


def _compute_mean_ROIs(stc, sbj_id, subjects_dir, parc,
                       forward, aseg, is_fixed):
    # these coo are in MRI space and we have to convert them to MNI space
    labels_cortex = mne.read_labels_from_annot(sbj_id, parc=parc,
                                               subjects_dir=subjects_dir)

    print(('\n*** %d ***\n' % len(labels_cortex)))

    src = forward['src']

    # allow_empty : bool -> Instead of emitting an error, return all-zero time
    # courses for labels that do not have any vertices in the source estimate

    if is_fixed:
        mode = 'mean_flip'
    else:
        mode = 'mean'

    label_ts = mne.extract_label_time_course(stc, labels_cortex, src,
                                             mode=mode,
                                             allow_empty=True,
                                             return_generator=False)

    # save results in .npy file that will be the input for spectral node
    print('\n*** SAVE ROI TS ***\n')
    print((len(label_ts)))

    if aseg:
        print(sbj_id)
        labels_aseg = get_volume_labels_from_src(src, sbj_id, subjects_dir)
        labels = labels_cortex + labels_aseg
    else:
        labels = labels_cortex
        labels_aseg = None

    print((labels[0].pos))
    print((len(labels)))

    labels_file, label_names_file, label_coords_file = \
        _create_MNI_label_files(forward, labels_cortex, labels_aseg,
                                sbj_id, subjects_dir)

    return label_ts, labels_file, label_names_file, label_coords_file
