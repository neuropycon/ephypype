"""Import ctf."""


# -------------------- nodes (Function)
def convert_ds_to_raw_fif(ds_file):
    """CTF .ds to .fif and save result in pipeline folder structure."""
    import os
    import os.path as op

    from nipype.utils.filemanip import split_filename as split_f
    from mne.io import read_raw_ctf

    _, basename, ext = split_f(ds_file)
    # print(subj_path, basename, ext)
    raw = read_raw_ctf(ds_file)
    # raw_fif_file = os.path.abspath(basename + "_raw.fif")

    # raw.save(raw_fif_file)
    # return raw_fif_file

    raw_fif_file = os.path.abspath(basename + "_raw.fif")

    if not op.isfile(raw_fif_file):
        raw = read_raw_ctf(ds_file)
        raw.save(raw_fif_file)
    else:
        print(('*** RAW FIF file %s exists!!!' % raw_fif_file))

    return raw_fif_file
