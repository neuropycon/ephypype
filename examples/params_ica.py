""" Parameters file for run_preprocess_pipeline.py """

data_type = 'ds'

main_path = '/home/mainak/Desktop/projects/github_repos/BIDS-examples/sample_BIDS_omega'
data_path = main_path

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
