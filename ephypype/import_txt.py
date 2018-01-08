# -*- coding: utf-8 -*-


def split_txt(sample_size, txt_file, sep_label_name, repair=True, sep=";", keep_electrodes=""):

    import os

    import numpy as np
    import pandas as pd

    if repair == True:

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

                # print splitted_line

                name = splitted_line[0]

                print(name)

                elec_names.append(name)

                #elec_names.append("".join(name.split(" ")))

                data = splitted_line[1]

                # print data

                # print len(data.split(sep))

                new_data = data.replace(" ", sep)

                df_data.append([float(data.replace(",", "."))
                                for data in new_data.split(sep)])

                # print df_data

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

            keep = np.array([len(index.split(sep_label_name))
                             == 2 for index in list_indexes], dtype="int")
        else:

            keep = np.array([len(index.split(sep_label_name)) ==
                             2 and index in list_keep_electrodes for index in list_indexes], dtype="int")
    else:
        if len(list_keep_electrodes) == 0:
            keep = np.ones(shape=np_indexes.shape)
        else:
            keep = np.array(
                [index in list_keep_electrodes for index in list_indexes], dtype="int")

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

        0 / 0

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


def read_brainvision_vhdr(vhdr_file, sample_size):

    import os
    import mne
    import numpy as np

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
