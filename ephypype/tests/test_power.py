from ephypype.power import compute_and_save_psd
import os


def test_power_welch():
    fmin = 0.1
    fmax = 300
    epochs_fname = 'test-epo.fif'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    epochs_fname_abs = os.path.join(dir_path, epochs_fname)
    compute_and_save_psd(epochs_fname_abs, fmin, fmax, method='welch')


def test_power_multitaper():
    fmin = 0.1
    fmax = 300
    epochs_fname = 'test-epo.fif'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    epochs_fname_abs = os.path.join(dir_path, epochs_fname)
    compute_and_save_psd(epochs_fname_abs, fmin, fmax, method='multitaper')
