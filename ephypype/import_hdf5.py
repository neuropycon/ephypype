#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 19:14:23 2018

@author: pasca
"""
import numpy as np
import h5py


def write_hdf5(filename, data, dataset_name='dataset', dtype='f'):
    """
    Create hdf5 file

    Inputs
        filename : str
            hdf5 filename
        data : array, shape (n_vertices, n_times)
            raw data for whose the dataset is created
        dataset_name : str
            name of dataset to create
        dtype : str
            data type for new dataset

    """

    hf = h5py.File(filename, 'w')
    hf.create_dataset(dataset_name, data=data, dtype=dtype)
    hf.close()


def read_hdf5(filename, dataset_name='dataset'):
    """
    Read hdf5 file

    Inputs
        filename : str
            hdf5 filename
        dataset_name : str
            name of dataset to create

    Outputs
        data : array, shape (n_vertices, n_times)
            raw data for whose the dataset is created
    """

    hf = h5py.File(filename, 'r')
    data = hf[dataset_name][()]

    return data


def npy2hdf5(filename, dataset_name='dataset', dtype='f'):

    data = np.load(filename)
    print('converting to hdf5')

    write_hdf5(filename, data, dataset_name=dataset_name, dtype=dtype)


def import_hdf5_file(hdf5_file, data_field_name='F'):

    import os
    import h5py
    import numpy as np
    from nipype.utils.filemanip import split_filename as split_f

    subj_path, basename, ext = split_f(hdf5_file)

    hf = h5py.File(hdf5_file, 'r')
    raw_data = hf[data_field_name][()]

    print(raw_data)
    print((raw_data.shape))
    print((raw_data.__class__))

    ts_file = os.path.abspath(basename + '.npy')
    np.save(ts_file, raw_data)

    return ts_file

     