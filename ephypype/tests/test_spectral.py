"""Test spectral."""

import numpy as np

from ephypype.spectral import (compute_spectral_connectivity,
                               compute_and_save_multi_spectral_connectivity)  # noqa

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


def test_compute_spectral_connectivity_one_trial():
    """Test compute_spectral_connectivity plv with one trial."""
    with pytest.raises(ValueError, message="Expecting ValueError"):
        compute_spectral_connectivity(data=ts_mat, con_method="plv",
                                      mode="multitaper", fmin=fmin, fmax=fmax,
                                      sfreq=sfreq, gathering_method='mean')


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
        compute_and_save_multi_spectral_connectivity(all_data=ts_mat,
                                                     con_method="coh",
                                                     mode="multitaper",
                                                     fmin=fmin, fmax=fmax,
                                                     sfreq=sfreq,
                                                     gathering_method='mean')
