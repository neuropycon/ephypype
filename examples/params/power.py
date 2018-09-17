""" Parameters file for run_power_analysis.py or run_src_power_analysis.py"""
import os.path as op
import ephypype
from ephypype.datasets import fetch_omega_dataset

base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_omega_dataset(base_path)

data_type = 'fif'
subject_ids = ['sub-0003']
sessions = ['ses-0001']

# -------------------------- SET power variables --------------------------#
freq_bands = [[2, 4], [5, 7], [8, 12], [13, 29], [30, 59], [60, 90]]
freq_band_names = ['delta', 'theta', 'alpha', 'beta', 'gamma1', 'gamma2']

is_epoched = False

fmin = 0.1
fmax = 150
sfreq = 600
power_method = 'welch'  # for sensor PSD
n_fft = 2048  # the FFT size (n_fft). Ideally a power of 2

if is_epoched:
    overlap = 0
else:
    overlap = 0.5

power_analysis_name = 'power_pipeline'
src_power_analysis_name = 'src_power_pipeline'

src_reconstruction_name = 'spectral_connectivity_fif_coh_src_space_MNE_aparc'

inv_solution_pipeline = 'inv_sol_pipeline'
inv_solution_node = 'inv_solution'
