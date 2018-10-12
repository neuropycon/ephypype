"""Test spectral."""
import os
import shutil
import numpy as np
import glob

from ephypype.spectral import (compute_spectral_connectivity,
                               compute_and_save_spectral_connectivity,
                               compute_and_save_multi_spectral_connectivity,
                               plot_circular_connectivity)  # noqa

import pytest

time_length = 10000
nb_ROI = 10

nb_trials = 50

sfreq = 500

fmin = 10
fmax = 300

ts_mat = np.random.rand(nb_ROI, time_length) * \
    np.random.choice([-1, 1], size=(nb_ROI, time_length))

ts_mat_trials = np.random.rand(nb_trials, nb_ROI, time_length) * \
    np.random.choice([-1, 1], size=(nb_trials, nb_ROI, time_length))

conmat = np.random.rand(nb_ROI, nb_ROI) * \
    np.random.choice([-1, 1], size=(nb_ROI, nb_ROI))

labels = [str(i) for i in range(nb_ROI)]

tmp_dir = "/tmp/test_ephypype"

if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)

os.makedirs(tmp_dir)


def test_compute_spectral_connectivity_one_trial():
    """Test compute_spectral_connectivity plv with one trial."""
    with pytest.raises(ValueError, message="Expecting ValueError"):
        compute_spectral_connectivity(data=ts_mat, con_method="plv",
                                      mode="multitaper", fmin=fmin, fmax=fmax,
                                      sfreq=sfreq, gathering_method='mean')


def test_compute_and_save_spectral_connectivity():
    compute_and_save_spectral_connectivity(data=ts_mat_trials,
                                           con_method="plv", mode="multitaper",
                                           fmin=fmin, fmax=fmax, sfreq=sfreq,
                                           gathering_method='mean',
                                           save_dir=tmp_dir)

    assert os.path.exists(os.path.join(tmp_dir, "conmat_0_plv.npy"))


def test_compute_spectral_connectivity_mean_max():
    """Test compute_spectral_connectivity mean and max."""
    res_mean = compute_spectral_connectivity(data=ts_mat_trials,
                                             con_method="coh",
                                             mode="multitaper", fmin=fmin,
                                             fmax=fmax, sfreq=sfreq,
                                             gathering_method='mean')

    res_max = compute_spectral_connectivity(data=ts_mat_trials,
                                            con_method="coh",
                                            mode="multitaper", fmin=fmin,
                                            fmax=fmax, sfreq=sfreq,
                                            gathering_method='max')

    assert np.all(res_mean <= res_max), ("error,\
        all mean values should be lower than max values")


def test_compute_and_save_multi_spectral_connectivity():
    """ testing compute_and_save_multi_spectral_connectivity"""
    with pytest.raises(AssertionError, message="Expecting AssertionError"):
        compute_and_save_multi_spectral_connectivity(
            all_data=ts_mat, con_method="coh", mode="multitaper", fmin=fmin,
            fmax=fmax, sfreq=sfreq, gathering_method='mean', save_dir=tmp_dir)

    compute_and_save_multi_spectral_connectivity(
        all_data=ts_mat_trials, con_method="coh", mode="multitaper", fmin=fmin,
        fmax=fmax, sfreq=sfreq, gathering_method='mean', save_dir=tmp_dir)

    list_coh_mat = glob.glob(os.path.join(tmp_dir, "conmat_*_coh.npy"))
    assert len(list_coh_mat) == nb_trials, ("Error {} \
        files".format(os.listdir(tmp_dir)))


def test_plot_circular_connectivity():
    """test plot_circular_connectivity"""
    plot_circular_connectivity(conmat, label_names=labels, save_dir=tmp_dir)

    assert os.path.exists(os.path.join(tmp_dir, "circle__def.eps")), "Error"
