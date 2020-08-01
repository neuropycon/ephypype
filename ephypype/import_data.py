"""Import data."""
import h5py
import os
import mne
import numpy as np

from nipype.utils.filemanip import split_filename as split_f
from scipy.io import loadmat
from mne.io import read_raw_ctf


# -------------------- nodes (Function)
def _convert_ds_to_raw_fif(ds_file):
    """CTF .ds to .fif and save result in pipeline folder structure."""

    _, basename, ext = split_f(ds_file)
    raw = read_raw_ctf(ds_file)

    raw_fif_file = os.path.abspath(basename + "_raw.fif")

    if not os.path.isfile(raw_fif_file):
        raw = read_raw_ctf(ds_file)
        raw.save(raw_fif_file)
    else:
        print(('*** RAW FIF file %s exists!!!' % raw_fif_file))

    return raw_fif_file


def _read_fieldtrip_epochs(epo_mat_file, data_field_name='data'):
    """Load epoched data from a FieldTrip structure contained in .mat file
    and save in .fif file"""

    _, basename, ext = split_f(epo_mat_file)
    assert os.path.isfile(epo_mat_file)

    epo = mne.read_epochs_fieldtrip(epo_mat_file, info=None,
                                    data_name=data_field_name)

    epo_fif_file = os.path.abspath(basename + "-epo.fif")
    epo.save(epo_fif_file, overwrite=True)
    print(('*** EPO file saved at % s' % epo_fif_file))

    return epo_fif_file


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


def _read_hdf5(filename, dataset_name='dataset', transpose=False):

    """
    Read hdf5 file

    Inputs
        filename : str
            hdf5 filename
        dataset_name : str
            name of dataset to create
        transpose: bool
            if the data needs to be transpose or not
    Outputs
        data : array, shape (n_vertices, n_times)
            raw data for whose the dataset is created
    """

    hf = h5py.File(filename, 'r')
    data = hf[dataset_name][()]

    if transpose:
        data = np.transpose(data)

    # old_path, basename, ext = split_f(filename)
    # npy_filename = os.path.abspath(basename + '.npy')
    # print(npy_filename)
    # np.save(npy_filename, data, allow_pickle=True)
    return data


def import_mat_to_conmat(mat_file, data_field_name='F',
                         orig_channel_names_file=None,
                         orig_channel_coords_file=None):
    """Import mat to conmat."""

    subj_path, basename, ext = split_f(mat_file)

    mat = loadmat(mat_file)

    if data_field_name not in mat.keys():
        data_field_name = basename.split('_')[0]
        assert data_field_name in mat.keys(), \
            ("error, could not find {}".format(data_field_name))

    raw_data = np.array(mat[data_field_name], dtype='f')
    print(raw_data)
    print((raw_data.shape))

    ts_file = os.path.abspath(basename + '.npy')
    np.save(ts_file, raw_data)

    if orig_channel_names_file is not None:

        elec_names = [line.strip() for line in open(orig_channel_names_file)]
        print(elec_names)

        # save channel names
        channel_names_file = os.path.abspath('correct_channel_names.txt')
        np.savetxt(channel_names_file, elec_names, fmt='%s')

    if orig_channel_coords_file is not None:
        correct_channel_coords = np.loadtxt(orig_channel_coords_file)
        print(correct_channel_coords)

        # save channel coords
        channel_coords_file = os.path.abspath('correct_channel_coords.txt')
        np.savetxt(channel_coords_file, correct_channel_coords, fmt='%s')

    return ts_file


def _import_tsmat_to_ts(tsmat_file, data_field_name='F',
                        good_channels_field_name=None,
                        orig_channel_names_file=None,
                        orig_channel_coords_file=None):
    """Import tsmat to ts."""

    print(tsmat_file)

    subj_path, basename, ext = split_f(tsmat_file)
    mat = loadmat(tsmat_file)

    if data_field_name not in mat.keys():

        data_field_name = basename.split('_')[0]

        assert data_field_name in mat.keys(), \
            ("error, could not find {}".format(data_field_name))

    raw_data = np.array(mat[data_field_name], dtype="f")
    print((raw_data.shape))

    print([key for key in list(mat.keys())])

    if good_channels_field_name is not None:

        assert good_channels_field_name in mat.keys(), \
            ("error, could not find {}".format(good_channels_field_name))
        print("Using good channels to sort channels")

        good_channels = np.array(mat[good_channels_field_name])
        print((good_channels.shape))

        good_channels = good_channels.reshape(good_channels.shape[0])
        print((good_channels.shape))

        good_data = raw_data[good_channels == 1, :]

    elif orig_channel_names_file is not None:

        # load electrode names
        assert os.path.exists(orig_channel_names_file), \
            ("Error, {} do not exists".format(orig_channel_names_file))
        print("Using orig_channel_names_file to sort channels")
        elec_names = [line.strip() for line in open(orig_channel_names_file)]
        print(elec_names)

        cond = [elec.startswith('EMG') or elec.startswith(
            'EOG') for elec in elec_names]
        select_sensors, = np.where(np.array(cond, dtype='bool') is False)
        print(select_sensors)

        # save electrode names
        correct_elec_names = np.array(
            [elec_names[pos] for pos in select_sensors],
            dtype="str")

        channel_names_file = os.path.abspath("correct_channel_names.txt")
        np.savetxt(channel_names_file, correct_elec_names, fmt='%s')

        if orig_channel_coords_file is not None:
            assert os.path.exists(orig_channel_coords_file), \
                ("Error, %s do not exists".format(orig_channel_coords_file))

            # save electrode locations
            elec_loc = np.loadtxt(orig_channel_coords_file)
            print(elec_loc)

            correct_elec_loc = np.roll(
                elec_loc[select_sensors, :], shift=2, axis=1)

            channel_coords_file = os.path.abspath("correct_channel_coords.txt")
            np.savetxt(channel_coords_file, correct_elec_loc, fmt='%s')

        # save data (reorganise dimensions)
        good_data = raw_data[select_sensors, :].swapaxes(0, 2).swapaxes(1, 2)

    else:
        print("No channel sorting")
        good_data = raw_data

    # save data
    print((good_data.shape))

    ts_file = os.path.abspath(basename + "_tsmat.npy")
    np.save(ts_file, good_data)

    return ts_file


def concat_ts(all_ts_files):
    """Concat ts."""
    for i, ts_file in enumerate(all_ts_files):

        # loading ROI coordinates
        ts = np.load(ts_file, allow_pickle=True)

        # print "all_ts: "
        print((ts.shape))

        if i == 0:
            concat_ts = ts.copy()
        else:
            concat_ts = np.concatenate((concat_ts, ts), axis=0)

    print((concat_ts.shape))

    # saving time series
    concat_ts_file = os.path.abspath("concat_ts.npy")
    np.save(concat_ts_file, concat_ts)

    return concat_ts_file


def _split_txt(sample_size, txt_file, sep_label_name, repair=True, sep=";",
               keep_electrodes=""):
    """Split txt."""
    import pandas as pd

    if repair is True:
        df_data = []
        elec_names = []

        with open(txt_file) as f:
            lines = f.readlines()
            for line in lines:
                # print line
                if line.startswith('"') and line.strip().endswith('"'):
                    line = line.strip()[1:-1]
                print(line)

                splitted_line = line.strip().split(sep, 1)
                name = splitted_line[0]
                print(name)

                elec_names.append(name)
                data = splitted_line[1]

                new_data = data.replace(" ", sep)
                df_data.append([float(d.replace(",", "."))
                                for d in new_data.split(sep)])

        print(df_data)
        print((np.array(df_data).shape))

        df = pd.DataFrame(np.array(df_data), index=elec_names)
    else:
        df = pd.read_table(txt_file, sep=sep, decimal=",",
                           header=None, index_col=0)

    # electrode names:
    np_indexes = df.index.values
    list_indexes = np_indexes.tolist()
    print(list_indexes)

    if keep_electrodes != "":
        list_keep_electrodes = keep_electrodes.split("-")
    else:
        list_keep_electrodes = []

    print(list_keep_electrodes)

    if sep_label_name != "":
        if len(list_keep_electrodes) == 0:

            keep = [len(index.split(
                        sep_label_name)) == 2 for index in list_indexes]
        else:

            keep = [len(index.split(sep_label_name)) == 2 and index in
                    list_keep_electrodes for index in list_indexes]
    else:
        if len(list_keep_electrodes) == 0:
            keep = np.ones(shape=np_indexes.shape)
        else:
            keep = [index in list_keep_electrodes for index in list_indexes]

    keep = keep.astype(int)
    print(keep)
    print((np_indexes[keep == 1]))

    elec_names_file = os.path.abspath("correct_channel_names.txt")
    np.savetxt(elec_names_file, np_indexes[keep == 1], fmt="%s")

    # splitting data_path
    print((df.shape))
    if df.shape[1] % sample_size != 0:
        print("Error, sample_size is not a multiple of ts shape")
        print(sample_size)
        print(df)
        return

    nb_epochs = df.shape[1] / sample_size
    print(nb_epochs)
    splitted_ts = np.split(df.values[keep == 1, :], nb_epochs, axis=1)
    print((len(splitted_ts)))
    print((splitted_ts[0]))

    np_splitted_ts = np.array(splitted_ts, dtype='float')
    print((np_splitted_ts.shape))

    splitted_ts_file = os.path.abspath("splitted_ts.npy")
    np.save(splitted_ts_file, np_splitted_ts)

    return splitted_ts_file, elec_names_file


def _read_brainvision_vhdr(vhdr_file, sample_size):
    """Read brainvision vhdr files."""
    data_raw = mne.io.read_raw_brainvision(vhdr_file, verbose=True)
    print((data_raw.ch_names))

    data, times = data_raw[:]
    print((data.shape))

    nb_epochs = data.shape[1] / sample_size
    print(nb_epochs)

    splitted_ts = np.split(data, nb_epochs, axis=1)
    print((len(splitted_ts)))
    print((splitted_ts[0]))

    np_splitted_ts = np.array(splitted_ts, dtype='float')
    print((np_splitted_ts.shape))

    return np_splitted_ts, data_raw.ch_names
