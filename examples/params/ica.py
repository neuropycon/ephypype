""" Parameters file for run_preprocess_pipeline.py """
import os.path as op
import ephypype
from ephypype.datasets import fetch_omega_dataset

data_type = 'ds'
base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_omega_dataset(base_path)

subject_ids = ['sub-0003']  # 'sub-0004', 'sub-0006'
sessions = ['ses-0001']

down_sfreq = 800
l_freq = 0.1
h_freq = 150


# ------------------------ SET ICA variables -----------------------------#

is_ICA = True  # if True we apply ICA to remove ECG and EoG artifacts

# specify ECG and EoG channel names if we know them
ECG_ch_name = 'ECG'
EoG_ch_name = 'HEOG, VEOG'
variance = 0.95

reject = dict(mag=5e-12, grad=5000e-13)

# pipeline directory within the main_path dir
preproc_pipeline_name = 'preprocessing_pipeline'
