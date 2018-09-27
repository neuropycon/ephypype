"""Test spectral."""

import numpy as np

import os
import shutil

import pytest

from ephypype.spectral import (compute_spectral_connectivity,
                               compute_and_save_multi_spectral_connectivity)  # noqa

import ephypype

print(ephypype.__path__)

print(ephypype.__version__)

#data_path = mne.datasets.sample.data_path()
#raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'

time_length = 10000
nb_ROI = 10

nb_trials = 50

sfreq = 500

fmin = 0.1
fmax = 300

ts_mat = np.random.rand(nb_ROI, time_length) * \
    np.random.choice([-1, 1], size=(nb_ROI, time_length))


ts_mat_trials = np.random.rand(nb_trials, nb_ROI, time_length) * \
    np.random.choice([-1, 1], size=(nb_trials, nb_ROI, time_length))

# testing compute_spectral_connectivit


def test_compute_spectral_connectivity_one_trial():
    """Test compute_spectral_connectivity plv with one trial."""
    with pytest.raises(SystemExit, message="OK caught SystemExit as expected for plv with one trial") as exception_one_plv:
        res_plv = compute_spectral_connectivity(
            data=ts_mat,
            con_method="plv",
            mode="multitaper",
            fmin=fmin,
            fmax=fmax,
            sfreq=sfreq,
            gathering_method='mean')

    print(exception_one_plv)


def test_compute_spectral_connectivity_mean_max():
    """Test compute_spectral_connectivity mean and max."""

    res_mean = compute_spectral_connectivity(
        data=ts_mat_trials,
        con_method="coh",
        mode="multitaper",
        fmin=fmin,
        fmax=fmax,
        sfreq=sfreq,
        gathering_method='mean')

    print(res_mean)
    res_max = compute_spectral_connectivity(
        data=ts_mat_trials,
        con_method="coh",
        mode="multitaper",
        fmin=fmin,
        fmax=fmax,
        sfreq=sfreq,
        gathering_method='max')

    print(res_max)

    assert np.all(
        res_mean <= res_max), "error, all mean values should be lower than max values"

# testing test_compute_and_save_multi_spectral_connectivity

tmp_dir = "/tmp/ephypype_test"


def test_compute_and_save_multi_spectral_connectivity():

    os.makedirs(tmp_dir)

    compute_and_save_multi_spectral_connectivity(
        all_data=ts_mat_trials,
        con_method="coh",
        mode="multitaper",
        fmin=fmin,
        fmax=fmax,
        sfreq=sfreq,
        gathering_method='mean',
        save_dir=tmp_dir)

    # list all created files
    tmp_files = os.listdir(tmp_dir)

    assert len(tmp_files) == nb_trials, "There should an equal number of files {} as trials {}".format(
        len(tmp_files), nb_trials)

    shutil.rmtree(tmp_dir)

if __name__ == '__main__':

    test_compute_spectral_connectivity_one_trial()
    # test_compute_spectral_connectivity_mean_max()

    # test_compute_and_save_multi_spectral_connectivity()
