# Created on Thu Oct  8 17:53:07 2015
# @author: pasca
import os.path as op
import numpy as np
import mne

from mne.io import read_raw_fif
from mne import read_epochs
from mne.minimum_norm import make_inverse_operator, apply_inverse_raw
from mne.minimum_norm import apply_inverse_epochs, apply_inverse
from mne import get_volume_labels_from_src
from mne import compute_raw_covariance, pick_types, write_cov

from nipype.utils.filemanip import split_filename as split_f

from .preproc import create_reject_dict
from .source_space import create_MNI_label_files
from .import_hdf5 import write_hdf5


def compute_noise_cov(cov_fname, raw):
    """
    Compute noise covariance data from a continuous segment of raw data.
    Employ empty room data (collected without the subject) to calculate
    the full noise covariance matrix.
    This is recommended for analyzing ongoing spontaneous activity.

    Inputs
        cov_fname : str
            noise covariance file name
        raw : Raw
            the raw data

    Output
        cov_fname : str
            noise covariance file name in which is saved the noise covariance
            matrix
    """

    print(('***** COMPUTE RAW COV *****' + cov_fname))

    if not op.isfile(cov_fname):

        data_path, basename, ext = split_f(raw.info['filename'])
        fname = op.join(data_path, '%s-cov.fif' % basename)

        reject = create_reject_dict(raw.info)

        picks = pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')

        noise_cov = compute_raw_covariance(raw, picks=picks, reject=reject)

        write_cov(fname, noise_cov)

    else:
        print(('*** NOISE cov file %s exists!!!' % cov_fname))

    return cov_fname


def read_noise_cov(cov_fname, raw_info):
    """
    Read a noise covariance matrix from cov_fname

    Inputs
        cov_fname : str
            noise covariance file name
        raw_info : dict
            dictionary containing the information about the raw data

    Outputs
        noise_cov : Covariance
            the noise covariance matrix
    """

    print(('***** READ RAW COV *****' + cov_fname))

    if not op.isfile(cov_fname):
        # create an Identity matrix
        picks = mne.pick_types(raw_info, meg=True, ref_meg=False,
                               exclude='bads')
        ch_names = [raw_info['ch_names'][i] for i in picks]

        C = mne.Covariance(data=np.identity(len(picks)), names=ch_names,
                           bads=[], projs=[], nfree=0)
        mne.write_cov(cov_fname, C)
    else:
        print(('*** noise covariance file %s exists!!!' % cov_fname))
        noise_cov = mne.read_cov(cov_fname)

    return noise_cov


'''
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| Inverse desired                             | Forward parameters allowed                 |  # noqa
+=====================+===========+===========+===========+=================+==============+
|                     | **loose** | **depth** | **fixed** | **force_fixed** | **surf_ori** |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Loose constraint, | 0.2       | 0.8       | False     | False           | True         |
| | Depth weighted    |           |           |           |                 |              |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Loose constraint  | 0.2       | None      | False     | False           | True         |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Free orientation, | None      | 0.8       | False     | False           | True         |
| | Depth weighted    |           |           |           |                 |              |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Free orientation  | None      | None      | False     | False           | True | False |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Fixed constraint, | None      | 0.8       | True      | False           | True         |
| | Depth weighted    |           |           |           |                 |              |
+---------------------+-----------+-----------+-----------+-----------------+--------------+
| | Fixed constraint  | None      | None      | True      | True            | True         |
+---------------------+-----------+-----------+-----------+-----------------+--------------+       
'''


def compute_inverse_solution(raw_filename, sbj_id, sbj_dir, fwd_filename,
                             cov_fname, is_epoched=False, events_id=[],
                             t_min=None, t_max=None, is_evoked=False,
                             snr=1.0, inv_method='MNE',
                             parc='aparc', aseg=False, aseg_labels=[],
                             all_src_space=False, ROIs_mean=True,
                             is_fixed=False):
    """
    Compute the inverse solution on raw/epoched data and return the average
    time series computed in the N_r regions of the source space defined by
    the specified cortical parcellation

    Inputs
        raw_filename : str
            filename of the raw/epoched data
        sbj_id : str
            subject name
        sbj_dir : str
            Freesurfer directory
        fwd_filename : str
            filename of the forward operator
        cov_filename : str
            filename of the noise covariance matrix
        is_epoched : bool
            if True and events_id = None the input data are epoch data
            in the format -epo.fif
            if True and events_id is not None, the raw data are epoched
            according to events_id and t_min and t_max values
        events_id: dict
            the dict of events
        t_min, t_max: int
            define the time interval in which to epoch the raw data
        is_evoked: bool
            if True the raw data will be averaged according to the events
            contained in the dict events_id
        inv_method : str
            the inverse method to use; possible choices: MNE, dSPM, sLORETA
        snr : float
            the SNR value used to define the regularization parameter
        parc: str
            the parcellation defining the ROIs atlas in the source space
        aseg: bool
            if True a mixed source space will be created and the sub cortical
            regions defined in aseg_labels will be added to the source space
        aseg_labels: list
            list of substructures we want to include in the mixed source space
        all_src_space: bool
            if True we compute the inverse for all points of the s0urce space
        ROIs_mean: bool
            if True we compute the mean of estimated time series on ROIs


    Outputs
        ts_file : str
            filename of the file where are saved the estimated time series
        labels_file : str
            filename of the file where are saved the ROIs of the parcellation
        label_names_file : str
            filename of the file where are saved the name of the ROIs of the
            parcellation
        label_coords_file : str
            filename of the file where are saved the coordinates of the
            centroid of the ROIs of the parcellation

    """

    try:
        traits.undefined(events_id)
    except NameError:
        events_id = None

    print(('\n*** READ raw filename %s ***\n' % raw_filename))
    if is_epoched and events_id is None:
        epochs = read_epochs(raw_filename)
        info = epochs.info
    else:
        raw = read_raw_fif(raw_filename, preload=True)
        info = raw.info

    subj_path, basename, ext = split_f(raw_filename)

    print(('\n*** READ noise covariance %s ***\n' % cov_fname))
    noise_cov = mne.read_cov(cov_fname)

    print(('\n*** READ FWD SOL %s ***\n' % fwd_filename))
    forward = mne.read_forward_solution(fwd_filename)

    # TODO check use_cps for force_fixed=True
    if not aseg:
        print(('\n*** fixed orientation {} ***\n'.format(is_fixed)))
        forward = mne.convert_forward_solution(forward, surf_ori=True,
                                               force_fixed=is_fixed,
                                               use_cps=False)

    lambda2 = 1.0 / snr ** 2

    # compute inverse operator
    print('\n*** COMPUTE INV OP ***\n')
    if is_fixed:
        loose = 0
        depth = None
        pick_ori = None
    elif aseg:
        loose = 1
        depth = None
        pick_ori = None
    else:
        loose = 0.2
        depth = 0.8
        pick_ori = 'normal'

    print(('\n *** loose {}  depth {} ***\n'.format(loose, depth)))
    inverse_operator = make_inverse_operator(info, forward, noise_cov,
                                             loose=loose, depth=depth,
                                             fixed=is_fixed)

    # apply inverse operator to the time windows [t_start, t_stop]s
    print('\n*** APPLY INV OP ***\n')
    if is_epoched and events_id is not None:
        events = mne.find_events(raw)
        picks = mne.pick_types(info, meg=True, eog=True, exclude='bads')
        reject = create_reject_dict(info)

        if is_evoked:
            epochs = mne.Epochs(raw, events, events_id, t_min, t_max,
                                picks=picks, baseline=(None, 0), reject=reject)
            evoked = [epochs[k].average() for k in events_id]
            snr = 3.0
            lambda2 = 1.0 / snr ** 2

            ev_list = list(events_id.items())
            for k in range(len(events_id)):
                stc = apply_inverse(evoked[k], inverse_operator, lambda2,
                                    inv_method, pick_ori=pick_ori)

                print(('\n*** STC for event %s ***\n' % ev_list[k][0]))
                stc_file = op.abspath(basename + '_' + ev_list[k][0])

                print('***')
                print(('stc dim ' + str(stc.shape)))
                print('***')

#                if not aseg:
#                    stc.save(stc_file)

        else:
            epochs = mne.Epochs(raw, events, events_id, t_min, t_max,
                                picks=picks, baseline=(None, 0), reject=reject)
            stc = apply_inverse_epochs(epochs, inverse_operator, lambda2,
                                       inv_method, pick_ori=pick_ori)

    elif is_epoched and events_id is None:
        stc = apply_inverse_epochs(epochs, inverse_operator, lambda2,
                                   inv_method, pick_ori=pick_ori)

    else:
        stc = apply_inverse_raw(raw, inverse_operator, lambda2, inv_method,
                                label=None,
                                start=None, stop=None,
                                buffer_size=1000,
                                pick_ori=pick_ori)  # None 'normal'

    if not isinstance(stc, list):
        print('***')
        print(('stc dim ' + str(stc.shape)))
        print('***')

        stc = [stc]
    else:
        print('***')
        print(('len stc %d' % len(stc)))
        print('***')

    print('**************************************************************')
    print('all_src_space: {}'.format(all_src_space))
    print('ROIs_mean: {}'.format(ROIs_mean))
    print('**************************************************************')
    if all_src_space:
        stc_data = list()
        stc_file = op.abspath(basename + '_stc.hdf5')

        for i in range(len(stc)):
            stc_data.append(stc[i].data)

            # TODO -> if memory error happens...
#            stc_file = op.abspath(basename + '_stc_' + str(i) + '.hdf5')
#            write_hdf5(stc_file, stc[i].data, dataset_name='stc_data')

        write_hdf5(stc_file, stc_data, dataset_name='stc_data')

    if ROIs_mean:
        label_ts, labels_file, label_names_file, label_coords_file = \
            _compute_mean_ROIs(stc, sbj_id, sbj_dir, parc, inverse_operator,
                               forward, aseg, is_fixed)

        ts_file = op.abspath(basename + '_ROI_ts.npy')
        np.save(ts_file, label_ts)

    else:
        ts_file = stc_file
        labels_file = ''
        label_names_file = ''
        label_coords_file = ''

    return ts_file, labels_file, label_names_file, label_coords_file


def _compute_mean_ROIs(stc, sbj_id, sbj_dir, parc, inverse_operator, forward,
                       aseg, is_fixed):
        # these coo are in MRI space and we have to convert to MNI space
    labels_cortex = mne.read_labels_from_annot(sbj_id, parc=parc,
                                               subjects_dir=sbj_dir)

    print(('\n*** %d ***\n' % len(labels_cortex)))

    src = inverse_operator['src']

    # allow_empty : bool -> Instead of emitting an error, return all-zero time
    # courses for labels that do not have any vertices in the source estimate

    if is_fixed:
        mode = 'mean_flip'
    else:
        mode = 'mean'

    label_ts = mne.extract_label_time_course(stc, labels_cortex, src,
                                             mode=mode,
                                             allow_empty=True,
                                             return_generator=False)

    # save results in .npy file that will be the input for spectral node
    print('\n*** SAVE ROI TS ***\n')
    print((len(label_ts)))

    if aseg:
        print(sbj_id)
        labels_aseg = get_volume_labels_from_src(src, sbj_id, sbj_dir)
        labels = labels_cortex + labels_aseg
    else:
        labels = labels_cortex
        labels_aseg = None

    print((labels[0].pos))
    print((len(labels)))

    labels_file, label_names_file, label_coords_file = \
        create_MNI_label_files(forward, labels_cortex, labels_aseg,
                               sbj_id, sbj_dir)

    return label_ts, labels_file, label_names_file, label_coords_file


def compute_ROIs_inv_sol(raw_filename, sbj_id, sbj_dir, fwd_filename,
                         cov_fname, is_epoched=False, events_id=[],
                         t_min=None, t_max=None, is_evoked=False,
                         snr=1.0, inv_method='MNE',
                         parc='aparc', aseg=False, aseg_labels=[],
                         save_stc=False, is_fixed=False):
    """
    Compute the inverse solution on raw/epoched data and return the average
    time series computed in the N_r regions of the source space defined by
    the specified cortical parcellation

    Inputs
        raw_filename : str
            filename of the raw/epoched data
        sbj_id : str
            subject name
        sbj_dir : str
            Freesurfer directory
        fwd_filename : str
            filename of the forward operator
        cov_filename : str
            filename of the noise covariance matrix
        is_epoched : bool
            if True and events_id = None the input data are epoch data
            in the format -epo.fif
            if True and events_id is not None, the raw data are epoched
            according to events_id and t_min and t_max values
        events_id: dict
            the dict of events
        t_min, t_max: int
            define the time interval in which to epoch the raw data
        is_evoked: bool
            if True the raw data will be averaged according to the events
            contained in the dict events_id
        inv_method : str
            the inverse method to use; possible choices: MNE, dSPM, sLORETA
        snr : float
            the SNR value used to define the regularization parameter
        parc: str
            the parcellation defining the ROIs atlas in the source space
        aseg: bool
            if True a mixed source space will be created and the sub cortical
            regions defined in aseg_labels will be added to the source space
        aseg_labels: list
            list of substructures we want to include in the mixed source space
        save_stc: bool
            if True the stc will be saved

    Outputs
        ts_file : str
            filename of the file where are saved the ROIs time series
        labels_file : str
            filename of the file where are saved the ROIs of the parcellation
        label_names_file : str
            filename of the file where are saved the name of the ROIs of the
            parcellation
        label_coords_file : str
            filename of the file where are saved the coordinates of the
            centroid of the ROIs of the parcellation

    """
    import os.path as op
    import numpy as np
    import mne

    from mne.io import read_raw_fif
    from mne import read_epochs
    from mne.minimum_norm import make_inverse_operator, apply_inverse_raw
    from mne.minimum_norm import apply_inverse_epochs, apply_inverse
    from mne import get_volume_labels_from_src

    from nipype.utils.filemanip import split_filename as split_f

    from ephypype.preproc import create_reject_dict
    from ephypype.source_space import create_MNI_label_files
    from ephypype.import_hdf5 import write_hdf5

    try:
        traits.undefined(events_id)
    except NameError:
        events_id = None

    print(('\n*** READ raw filename %s ***\n' % raw_filename))
    if is_epoched and events_id is None:
        epochs = read_epochs(raw_filename)
        info = epochs.info
    else:
        raw = read_raw_fif(raw_filename, preload=True)
#        raw.set_eeg_reference()
        info = raw.info

    subj_path, basename, ext = split_f(raw_filename)

    print(('\n*** READ noise covariance %s ***\n' % cov_fname))
    noise_cov = mne.read_cov(cov_fname)

    print(('\n*** READ FWD SOL %s ***\n' % fwd_filename))
    forward = mne.read_forward_solution(fwd_filename)

    if not aseg:
        print(('\n*** fixed orientation {} ***\n'.format(is_fixed)))
        forward = mne.convert_forward_solution(forward, surf_ori=True,
                                               force_fixed=is_fixed)

    lambda2 = 1.0 / snr ** 2

    # compute inverse operator
    print('\n*** COMPUTE INV OP ***\n')
    if is_fixed:
        loose = 0
        depth = None
        pick_ori = None
    elif aseg:
        loose = 1
        depth = None
        pick_ori = None
    else:
        loose = 0.2
        depth = 0.8
        pick_ori = 'normal'

    print(('\n *** loose {}  depth {} ***\n'.format(loose, depth)))
    inverse_operator = make_inverse_operator(info, forward, noise_cov,
                                             loose=loose, depth=depth,
                                             fixed=is_fixed)

    # apply inverse operator to the time windows [t_start, t_stop]s
    print('\n*** APPLY INV OP ***\n')
    if is_epoched and events_id is not None:
        events = mne.find_events(raw)
        picks = mne.pick_types(info, meg=True, eog=True, exclude='bads')
        reject = create_reject_dict(info)

        if is_evoked:
            epochs = mne.Epochs(raw, events, events_id, t_min, t_max,
                                picks=picks, baseline=(None, 0), reject=reject)
            evoked = [epochs[k].average() for k in events_id]
            snr = 3.0
            lambda2 = 1.0 / snr ** 2

            ev_list = list(events_id.items())
            for k in range(len(events_id)):
                stc = apply_inverse(evoked[k], inverse_operator, lambda2,
                                    inv_method, pick_ori=pick_ori)

                print(('\n*** STC for event %s ***\n' % ev_list[k][0]))
                stc_file = op.abspath(basename + '_' + ev_list[k][0])

                print('***')
                print(('stc dim ' + str(stc.shape)))
                print('***')

                if not aseg:
                    stc.save(stc_file)

        else:
            epochs = mne.Epochs(raw, events, events_id, t_min, t_max,
                                picks=picks, baseline=(None, 0), reject=reject)
            stc = apply_inverse_epochs(epochs, inverse_operator, lambda2,
                                       inv_method, pick_ori=pick_ori)

            print('***')
            print(('len stc %d' % len(stc)))
            print('***')

    elif is_epoched and events_id is None:
        stc = apply_inverse_epochs(epochs, inverse_operator, lambda2,
                                   inv_method, pick_ori=pick_ori)
        print('***')
        print(('len stc %d' % len(stc)))
        print('***')
    else:
        stc = apply_inverse_raw(raw, inverse_operator, lambda2, inv_method,
                                label=None,
                                start=None, stop=None,
                                buffer_size=1000,
                                pick_ori=pick_ori)  # None 'normal'

        print('***')
        print(('stc dim ' + str(stc.shape)))
        print('***')

    if not isinstance(stc, list):
        stc = [stc]

    if save_stc:
        for i in range(len(stc)):
            stc_file = op.abspath(basename + '_stc_' + str(i) + '.hdf5')
            write_hdf5(stc_file, stc[i].data, dataset_name='stc_data')

    # these coo are in MRI space and we have to convert to MNI space
    labels_cortex = mne.read_labels_from_annot(sbj_id, parc=parc,
                                               subjects_dir=sbj_dir)

    print(('\n*** %d ***\n' % len(labels_cortex)))

    src = inverse_operator['src']

    # allow_empty : bool -> Instead of emitting an error, return all-zero time
    # courses for labels that do not have any vertices in the source estimate

    if is_fixed:
        mode = 'mean_flip'
    else:
        mode = 'mean'

    label_ts = mne.extract_label_time_course(stc, labels_cortex, src,
                                             mode=mode,
                                             allow_empty=True,
                                             return_generator=False)

    # save results in .npy file that will be the input for spectral node
    print('\n*** SAVE ROI TS ***\n')
    print((len(label_ts)))

    ts_file = op.abspath(basename + '_ROI_ts.npy')
    np.save(ts_file, label_ts)

    if aseg:
        print(sbj_id)
        labels_aseg = get_volume_labels_from_src(src, sbj_id, sbj_dir)
        labels = labels_cortex + labels_aseg
    else:
        labels = labels_cortex
        labels_aseg = None

    print((labels[0].pos))
    print((len(labels)))

    # labels_file, label_names_file, label_coords_file = \
    # create_label_files(labels)
    labels_file, label_names_file, label_coords_file = \
        create_MNI_label_files(forward, labels_cortex, labels_aseg,
                               sbj_id, sbj_dir)

    return ts_file, labels_file, label_names_file, label_coords_file
