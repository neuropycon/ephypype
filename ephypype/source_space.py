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

    import mne
    import numpy as np

    ROI_MNI_coords = list()
    ROI_name = list()

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

    ROI_MNI = dict(ROI_name=ROI_name, ROI_MNI_coords=ROI_MNI_coords)

    return ROI_MNI


# ASEG coo head -> MNI
def convert_aseg_head_to_MNI(fwd, sbj, sbj_dir):

    import mne
    from mne.transforms import apply_trans, invert_transform

    fwd_src = fwd['src']

    ROI_aseg_MNI_coords = list()
    ROI_aseg_name = list()

    # get the MRI (surface RAS) -> head matrix
    mri_head_t = fwd['mri_head_t']
    head_mri_t = invert_transform(mri_head_t)  # head->MRI (surface RAS)
    for s in fwd_src[2:]:
        print('sub structure {} \n'.format(s['seg_name']))
        # before we go from head to MRI (surface RAS)
        aseg_coo = s['rr'][s['vertno']]
        aseg_coo_MRI_RAS = apply_trans(head_mri_t, aseg_coo)
        coo_MNI, _ = mne.aseg_vertex_to_mni(aseg_coo_MRI_RAS*1000,
                                            sbj, sbj_dir)
        ROI_aseg_MNI_coords.append(coo_MNI)
        ROI_aseg_name.append(s['seg_name'])

    ROI_MNI = dict(ROI_aseg_name=ROI_aseg_name,
                   ROI_aseg_MNI_coords=ROI_aseg_MNI_coords)

    return ROI_MNI

    