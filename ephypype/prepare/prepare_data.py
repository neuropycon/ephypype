# -*- coding: utf-8 -*-


def format_electrodes_xls(data_path, xls_electrodes_file):

    electrode_file = os.path.join(data_path, xls_electrodes_file)

    df = pd.read_excel(electrode_file)

    print(df)

    # remove all empty lines (only nans)

    df = df.dropna(how='all')

    print(df)

    # replace ratid for all subsequent lines (use for groupby at the end)

    animal_id = 0

    print((df.shape))

    for i in df.index:

        if pd.notnull(df["animal"][i]):

            animal_id = df["animal"][i]

        else:
            df.loc[i, "animal"] = animal_id

        print(animal_id)

    print(df)

    # replacing each electrode by new name, or by -1 if does not exists

    df.loc[pd.notnull(df["replace or remove"]),
           "name_brain region"] = df["replace or remove"][pd.notnull(df["replace or remove"])]

    # saving each rat independtly

    for animal_id in np.unique(df['animal']):

        print(animal_id)

        rat_electrode_file = os.path.join(
            data_path, animal_id + "_electrode_modif.txt")

        print(rat_electrode_file)

        # make a df from the data
        df_rat = df.loc[df['animal'] == animal_id]

        print(df_rat)

        # export the name_brain region
        name_elec = df_rat["name_brain region"]

        np.savetxt(rat_electrode_file, name_elec, fmt="%s")
