"""Source space functions."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import mne
import pickle
import numpy as np
import os.path as op


def get_roi(labels_cortex, vertno_left, vertno_right):
    """Get roi."""
    label_vertidx = list()
    label_name = list()
    label_coords = list()

    for label in labels_cortex:
        if label.hemi == 'lh':
            this_vertno = np.intersect1d(vertno_left, label.vertices)
            vertidx_hemi = np.searchsorted(vertno_left, this_vertno)

        elif label.hemi == 'rh':
            this_vertno = np.intersect1d(vertno_right, label.vertices)
            vertidx_hemi = len(vertno_left) + \
                np.searchsorted(vertno_right, this_vertno)

        vertidx_roi = np.searchsorted(label.vertices, this_vertno)
        label_vertidx.append(vertidx_hemi)
        label_name.append(label.name)
        label_coords.append(label.pos[vertidx_roi, :] * 1000)

    roi = dict(label_name=label_name, label_vertidx=label_vertidx,
               label_coords=label_coords)

    return roi


# convert the ROI coords to MNI space
def convert_cortex_mri_to_mni(labels_cortex, vertno_left, vertno_right,
                              sbj, subjects_dir):
    """Convert the coordinates of the ROIs cortex to MNI space.

    Parameters
    ----------
    labels_cortex : list
        List of labels.
    """
    roi_mni_coords = list()
    roi_name = list()
    roi_color = list()

    # labels_cortex is in MRI (surface RAS) space
    for label in labels_cortex:
        if label.hemi == 'lh':
            # from MRI (surface RAS) -> MNI
            roi_coo_mni = mne.vertex_to_mni(label.vertices, 0, sbj,
                                            subjects_dir)

            # get the vertices of the ROI used in the src space (index points
            # to dense src space of FS segmentation)
            this_vertno = np.intersect1d(vertno_left, label.vertices)
        elif label.hemi == 'rh':
            roi_coo_mni = mne.vertex_to_mni(label.vertices, 1, sbj,
                                            subjects_dir)

            this_vertno = np.intersect1d(vertno_right, label.vertices)

        # find
        vertidx_roi = np.searchsorted(label.vertices, this_vertno)

        roi_mni_coords.append(roi_coo_mni[vertidx_roi, :])
        roi_name.append(label.name)
        roi_color.append(label.color)

    # TODO check!
    #    nvert_ROI = [len(vn) for vn in roi_mni_coords]
    #    if np.sum(nvert_ROI) != (len(vertno_left) + len(vertno_right)):
    #        raise RuntimeError('number of src space vertices must be equal \
    #                            to the total number of ROI vertices')

    roi_mni = dict(ROI_name=roi_name, ROI_MNI_coords=roi_mni_coords,
                   ROI_color=roi_color)

    return roi_mni


# ASEG coo head -> MNI
def convert_aseg_head_to_mni(labels_aseg, mri_head_t, sbj, subjects_dir):
    """Convert the coordinates of substructures vol from head coordinate system
        to MNI ones to MNI."""
    ROI_aseg_MNI_coords = list()
    ROI_aseg_name = list()
    ROI_aseg_color = list()

    # get the MRI (surface RAS) -> head matrix
    # head_mri_t = invert_transform(mri_head_t)  # head->MRI (surface RAS)
    for label in labels_aseg:
        print(('sub structure {} \n'.format(label.name)))
        # Convert coo from head coordinate system to MNI ones.
        aseg_coo = label.pos
        coo_MNI = mne.head_to_mni(aseg_coo, sbj, mri_head_t, subjects_dir)

        ROI_aseg_MNI_coords.append(coo_MNI)
        ROI_aseg_name.append(label.name)
        ROI_aseg_color.append(label.color)

    nvert_roi = [len(vn) for vn in ROI_aseg_MNI_coords]
    nvert_src = [l.pos.shape[0] for l in labels_aseg]
    if np.sum(nvert_roi) != np.sum(nvert_src):
        raise RuntimeError('number of vol src space vertices must be equal to \
                            the total number of ROI vertices')

    roi_mni = dict(ROI_aseg_name=ROI_aseg_name,
                   ROI_aseg_MNI_coords=ROI_aseg_MNI_coords,
                   ROI_aseg_color=ROI_aseg_color)

    return roi_mni


def create_label_files(labels):
    """Create label files."""
    labels_file = op.abspath('labels.dat')
    with open(labels_file, "wb") as f:
        pickle.dump(len(labels), f)
        for value in labels:
            pickle.dump(value, f)

    label_names_file = op.abspath('label_names.txt')
    label_coords_file = op.abspath('label_coords.txt')

    label_names = []
    label_coords = []

    for value in labels:
        label_names.append(value.name)
#        label_coords.append(value.pos[0])
        label_coords.append(np.mean(value.pos, axis=0))

    np.savetxt(label_names_file, np.array(label_names, dtype=str),
               fmt="%s")
    np.savetxt(label_coords_file, np.array(label_coords, dtype=float),
               fmt="%f %f %f")

    return labels_file, label_names_file, label_coords_file


def _create_MNI_label_files(fwd, labels_cortex, labels_aseg, sbj,
                            subjects_dir):
    """Create MNI label files."""
    print(('*** n labels cortex: {} ***'.format(len(labels_cortex))))
    if labels_aseg:
        print(('*** n labels aseg: {} ***'.format(len(labels_aseg))))
    else:
        print('*** no deep regions ***')
    label_names_file = op.abspath('label_names.txt')
    label_coords_file = op.abspath('label_coords.txt')
    label_centroid_file = op.abspath('label_centroid.txt')

    label_names = list()
    label_centroids = list()

    vertno_left = fwd['src'][0]['vertno']
    vertno_right = fwd['src'][1]['vertno']

    roi_cortex = convert_cortex_mri_to_mni(labels_cortex, vertno_left,
                                           vertno_right, sbj, subjects_dir)
    roi_cortex_name = roi_cortex['ROI_name']
    roi_cortex_mni_coords = roi_cortex['ROI_MNI_coords']
    roi_cortex_color = roi_cortex['ROI_color']

    if labels_aseg:
        roi_aseg = convert_aseg_head_to_mni(labels_aseg, fwd['mri_head_t'],
                                            sbj, subjects_dir)
        roi_aseg_mni_coords = roi_aseg['ROI_aseg_MNI_coords']
        roi_aseg_name = roi_aseg['ROI_aseg_name']
        roi_aseg_color = roi_aseg['ROI_aseg_color']
    else:
        roi_aseg_name = []
        roi_aseg_mni_coords = []
        roi_aseg_color = []

    # ROI names
    roi_names = roi_cortex_name + roi_aseg_name
    for name in roi_names:
        label_names.append(name)
    np.savetxt(label_names_file, np.array(label_names, dtype=str),
               fmt="%s")

    # ROI centroids
    roi_coords = roi_cortex_mni_coords + roi_aseg_mni_coords
    for coo in roi_coords:
        label_centroids.append(np.mean(coo, axis=0))
    np.savetxt(label_centroid_file, np.array(label_centroids, dtype=float),
               fmt="%f %f %f")

    # ROI MNI coords
    label_coo_mni_matrix = np.vstack(roi_coords)
    np.savetxt(label_coords_file, np.array(label_coo_mni_matrix, dtype=float),
               fmt="%f %f %f")

    roi_colors = roi_cortex_color + roi_aseg_color

    roi = dict(ROI_names=roi_names, ROI_coords=roi_coords,
               ROI_colors=roi_colors)

    print(('*** written {} labels in a pickle ***'.format(len(roi_names))))
    labels_file = op.abspath('labels.pkl')
    with open(labels_file, "wb") as f:
        pickle.dump(roi, f)

    return labels_file, label_names_file, label_coords_file
