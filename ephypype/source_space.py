# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 18:33:28 2017

@author: pasca
"""


def get_ROI(labels_cortex, vertno_left, vertno_right):

    import numpy as np

    label_vertidx = list()
    label_name = list()
    label_coords = list()    

    for label in labels_cortex:
        if label.hemi == 'lh':
            this_vertno = np.intersect1d(vertno_left, label.vertices)
            vertidx_hemi = np.searchsorted(vertno_left, this_vertno)
            
        elif label.hemi == 'rh':
            this_vertno = np.intersect1d(vertno_right, label.vertices)
            vertidx_hemi = len(vertno_left) + np.searchsorted(vertno_right,this_vertno)

        vertidx_ROI = np.searchsorted(label.vertices, this_vertno)
        label_vertidx.append(vertidx_hemi)
        label_name.append(label.name)
        label_coords.append(label.pos[vertidx_ROI, :]*1000)

    ROI = dict(label_name=label_name, label_vertidx=label_vertidx,
               label_coords=label_coords)

    return ROI


# convert the ROI coords to MNI space
def convert_cortex_MRI_to_MNI(labels_cortex, vertno_left, vertno_right,
                              sbj, sbj_dir):

    """
    Convert the coordinates of the ROIs cortex to MNI space

    Inputs
        labels_cortex : list of Label

    """
    import mne
    import numpy as np

    ROI_MNI_coords = list()
    ROI_name = list()
    ROI_color = list()

    # labels_cortex is in MRI (surface RAS) space
    for label in labels_cortex:
        if label.hemi == 'lh':
            # from MRI (surface RAS) -> MNI
            ROI_coo_MNI, _ = mne.vertex_to_mni(label.vertices, 0, sbj, sbj_dir)

            # get the vertices of the ROI used in the src space (index points
            # to dense src space of FS segmentation)
            this_vertno = np.intersect1d(vertno_left, label.vertices)
        elif label.hemi == 'rh':
            ROI_coo_MNI, _ = mne.vertex_to_mni(label.vertices, 1, sbj, sbj_dir)

            this_vertno = np.intersect1d(vertno_right, label.vertices)

        # find
        vertidx_ROI = np.searchsorted(label.vertices, this_vertno)

        ROI_MNI_coords.append(ROI_coo_MNI[vertidx_ROI, :])
        ROI_name.append(label.name)
        ROI_color.append(label.color)

    nvert_ROI = [len(vn) for vn in ROI_MNI_coords]

    if np.sum(nvert_ROI) != (len(vertno_left) + len(vertno_right)):
        raise RuntimeError('number of src space vertices must be equal to \
                            the total number of ROI vertices')

    ROI_MNI = dict(ROI_name=ROI_name, ROI_MNI_coords=ROI_MNI_coords,
                   ROI_color=ROI_color)

    return ROI_MNI


# ASEG coo head -> MNI
def convert_aseg_head_to_MNI(labels_aseg, mri_head_t, sbj, sbj_dir):

    import mne
    import numpy as np
    from mne.transforms import apply_trans, invert_transform

    ROI_aseg_MNI_coords = list()
    ROI_aseg_name = list()
    ROI_aseg_color = list()

    # get the MRI (surface RAS) -> head matrix
    head_mri_t = invert_transform(mri_head_t)  # head->MRI (surface RAS)
    for label in labels_aseg:
        print('sub structure {} \n'.format(label.name))
        # before we go from head to MRI (surface RAS)
        aseg_coo = label.pos
        aseg_coo_MRI_RAS = apply_trans(head_mri_t, aseg_coo)
        coo_MNI, _ = mne.aseg_vertex_to_mni(aseg_coo_MRI_RAS*1000,
                                            sbj, sbj_dir)
        ROI_aseg_MNI_coords.append(coo_MNI)
        ROI_aseg_name.append(label.name)
        ROI_aseg_color.append(label.color)

    nvert_ROI = [len(vn) for vn in ROI_aseg_MNI_coords]
    nvert_src = [l.pos.shape[0] for l in labels_aseg]
    if np.sum(nvert_ROI) != np.sum(nvert_src):
        raise RuntimeError('number of vol ssrc space vertices must be equal to \
                            the total number of ROI vertices')

    ROI_MNI = dict(ROI_aseg_name=ROI_aseg_name,
                   ROI_aseg_MNI_coords=ROI_aseg_MNI_coords,
                   ROI_aseg_color=ROI_aseg_color)

    return ROI_MNI


def create_label_files(labels):
    import pickle
    import numpy as np
    import os.path as op

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


def create_MNI_label_files(fwd, labels_cortex, labels_aseg, sbj, sbj_dir):
    import pickle
    import numpy as np
    import os.path as op

    label_names_file = op.abspath('label_names.txt')
    label_coords_file = op.abspath('label_coords.txt')

    label_names = list()
    label_coords = list()

    vertno_left = fwd['src'][0]['vertno']
    vertno_right = fwd['src'][1]['vertno']

    ROI_cortex = convert_cortex_MRI_to_MNI(labels_cortex, vertno_left,
                                           vertno_right, sbj, sbj_dir)
    ROI_cortex_name = ROI_cortex['ROI_name']
    ROI_cortex_MNI_coords = ROI_cortex['ROI_MNI_coords']
    ROI_cortex_color = ROI_cortex['ROI_color']

    ROI_aseg = convert_aseg_head_to_MNI(labels_aseg, fwd['mri_head_t'],
                                        sbj, sbj_dir)
    ROI_aseg_MNI_coords = ROI_aseg['ROI_aseg_MNI_coords']
    ROI_aseg_name = ROI_aseg['ROI_aseg_name']
    ROI_aseg_color = ROI_aseg['ROI_color']

    # ROI names
    ROI_names = ROI_cortex_name + ROI_aseg_name
    for name in ROI_names:
        label_names.append(name)
    np.savetxt(label_names_file, np.array(label_names, dtype=str),
               fmt="%s")

    # ROI centroids
    ROI_coords = ROI_cortex_MNI_coords + ROI_aseg_MNI_coords
    for coo in ROI_coords:
        label_coords.append(np.mean(coo, axis=0))
    np.savetxt(label_coords_file, np.array(label_coords, dtype=float),
               fmt="%f %f %f")

    ROI_colors = ROI_cortex_color + ROI_aseg_color
    ROI = dict(ROI_names=ROI_names, ROI_coords=ROI_coords,
               ROI_colors=ROI_colors)

    labels_file = op.abspath('labels.pkl')
    with open(labels_file, "wb") as f:
        pickle.dump(ROI, f)

    return labels_file, label_names_file, label_coords_file
