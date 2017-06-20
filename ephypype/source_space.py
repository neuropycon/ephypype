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
    

def convert_to_MNI(labels_cortex, vertno_left, vertno_right, sbj, sbj_dir):

    import mne
    import numpy as np

    ROI_MNI_coords = list()
    ROI_name = list()

    for label in labels_cortex:
        if label.hemi == 'lh':
            ROI_coo_MNI, _ = mne.vertex_to_mni(label.vertices, 0, sbj, sbj_dir)

            this_vertno = np.intersect1d(vertno_left, label.vertices)
        elif label.hemi == 'rh':
            ROI_coo_MNI, _ = mne.vertex_to_mni(label.vertices, 1, sbj, sbj_dir)

            this_vertno = np.intersect1d(vertno_right, label.vertices)

        vertidx_ROI = np.searchsorted(label.vertices, this_vertno)

        ROI_MNI_coords.append(ROI_coo_MNI[vertidx_ROI, :])
        ROI_name.append(label.name)
        
    ROI_MNI = dict(ROI_name=ROI_name, ROI_MNI_coords=ROI_MNI_coords)
    
    return ROI_MNI
