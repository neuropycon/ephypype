"""
Inverse Solution Pipeline
"""
# Author: Annalisa Pascarella <a.pascarella@iac.cnr.it>

import nipype.pipeline.engine as pe

from nipype.interfaces.utility import IdentityInterface

from ..interfaces.mne.LF_computation import LFComputation
from ..interfaces.mne.Inverse_solution import NoiseCovariance
from ..interfaces.mne.Inverse_solution import InverseSolution
from ..interfaces.mne.preproc import DefineEpochs


def create_pipeline_source_reconstruction(main_path, subjects_dir,
                                          pipeline_name='inv_sol_pipeline',
                                          spacing='ico-5',
                                          inv_method='MNE',
                                          snr=1.0,
                                          is_epoched=False,
                                          events_id={},
                                          condition=None,
                                          decim=1,
                                          t_min=None, t_max=None,
                                          is_evoked=False,
                                          parc='aparc',
                                          aseg=False,
                                          aseg_labels=[],
                                          noise_cov_fname='',
                                          all_src_space=False,
                                          ROIs_mean=True,
                                          save_mixed_src_space=False,
                                          is_fixed=False):
    """Source reconstruction pipeline.

    Parameters
    ----------
    main_path : str
        the main path of the workflow
    subjects_dir : str
        Freesurfer directory
    pipeline_name : str (default inv_sol_pipeline)
        name of the pipeline
    spacing : str (default 'ico-5')
        spacing to use to setup a source space
    inv_method : str (default MNE)
        the inverse method to use; possible choices: MNE, dSPM, sLORETA
    is_epoched : bool (default False)
        if True and events_id = None the input data are epoch data
        in the format -epo.fif
        if True and events_id is not None, the raw data are epoched
        according to events_id and t_min and t_max values
    is_fixed : bool (default False)
        if True we use fixed orientation, otherwise the loose orientation
        is applied
    events_id: dict (default None)
        the dict of events
    t_min, t_max: int (defualt None)
        define the time interval in which to epoch the raw data
    is_evoked: bool (default False)
        if True the raw data will be averaged according to the events
        contained in the dict events_id
    parc: str (default 'aparc')
        the parcellation defining the ROIs atlas in the source space
    aseg: bool (defualt False)
        if True a mixed source space will be created and the sub cortical
        regions defined in aseg_labels will be added to the source space
    aseg_labels: list (default [])
        list of substructures we want to include in the mixed source space
    noise_cov_fname: str (default None)
        template for the path to either the noise covariance matrix file or
        the empty room data
    all_src_space: bool
        if True we compute the inverse for all points of the source space
    ROIs_mean: bool
        if True we compute the mean of estimated time series on ROIs
    save_mixed_src_space: bool (defualt False)
        if True the mixed src space will be saved in the FS folder

    raw (inputnode): str
        path to raw data in fif format
    sbj_id (inputnode): str
        subject id

    Returns
    -------
    pipeline : instance of Workflow
    """

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    inputnode = pe.Node(IdentityInterface(fields=['sbj_id', 'raw',
                                                  'trans_file',
                                                  'events_file']),
                        name='inputnode')

    # Lead Field computation Node
    LF_computation = pe.Node(interface=LFComputation(), name='LF_computation')
    LF_computation.inputs.subjects_dir = subjects_dir
    LF_computation.inputs.spacing = spacing
    LF_computation.inputs.aseg = aseg
    if aseg:
        LF_computation.inputs.aseg_labels = aseg_labels
        LF_computation.inputs.save_mixed_src_space = save_mixed_src_space

    pipeline.connect(inputnode, 'sbj_id', LF_computation, 'sbj_id')
    pipeline.connect(inputnode, 'raw', LF_computation, 'raw_fname')
    pipeline.connect(inputnode, 'trans_file', LF_computation, 'trans_file')

    # Create epochs based on events_id
    if is_epoched and events_id != {}:
        define_epochs = pe.Node(interface=DefineEpochs(), name='define_epochs')
        define_epochs.inputs.events_id = events_id
        define_epochs.inputs.t_min = t_min
        define_epochs.inputs.t_max = t_max
        define_epochs.inputs.decim = decim

        pipeline.connect(inputnode, 'raw', define_epochs, 'fif_file')
        pipeline.connect(inputnode, 'events_file', define_epochs, 'events_file')  # noqa

    # Noise Covariance Matrix Node
    create_noise_cov = pe.Node(interface=NoiseCovariance(),
                               name="create_noise_cov")

    print('******************** {}', noise_cov_fname)
    create_noise_cov.inputs.cov_fname_in = noise_cov_fname
    create_noise_cov.inputs.is_epoched = is_epoched
    create_noise_cov.inputs.is_evoked = is_evoked

    if is_epoched and is_evoked:
        pipeline.connect(define_epochs, 'epo_fif_file',
                         create_noise_cov, 'raw_filename')
    else:
        pipeline.connect(inputnode, 'raw', create_noise_cov, 'raw_filename')

    # Inverse Solution Node
    inv_solution = pe.Node(interface=InverseSolution(), name='inv_solution')

    inv_solution.inputs.subjects_dir = subjects_dir
    inv_solution.inputs.inv_method = inv_method
    inv_solution.inputs.is_epoched = is_epoched
    inv_solution.inputs.is_fixed = is_fixed
    inv_solution.inputs.snr = snr
    if is_evoked:
        inv_solution.inputs.events_id = events_id
        inv_solution.inputs.is_evoked = is_evoked
        if condition:
            inv_solution.inputs.condition = condition

    inv_solution.inputs.parc = parc
    inv_solution.inputs.aseg = aseg
    if aseg:
        inv_solution.inputs.aseg_labels = aseg_labels

    inv_solution.inputs.all_src_space = all_src_space
    inv_solution.inputs.ROIs_mean = ROIs_mean

    pipeline.connect(inputnode, 'sbj_id', inv_solution, 'sbj_id')
    if is_epoched and is_evoked:
        pipeline.connect(define_epochs, 'epo_fif_file',
                         inv_solution, 'raw_filename')
    else:
        pipeline.connect(inputnode, 'raw', inv_solution, 'raw_filename')
    pipeline.connect(LF_computation, 'fwd_filename',
                     inv_solution, 'fwd_filename')
    pipeline.connect(create_noise_cov, 'cov_fname_out',
                     inv_solution, 'cov_filename')

    return pipeline


def create_pipeline_evoked_inverse_solution(main_path, subjects_dir,
                                            pipeline_name='evoked_inv_sol_pipeline',  # noqa
                                            spacing='ico-5',
                                            inv_method='MNE',
                                            snr=3.0,
                                            parc='aparc',
                                            aseg=False,
                                            aseg_labels=[],
                                            all_src_space=False,
                                            ROIs_mean=True,
                                            save_mixed_src_space=False,
                                            is_fixed=False,
                                            noise_cov_fname='',
                                            events_id={},
                                            condition=None):
    """Source reconstruction pipeline.

    Parameters
    ----------
    main_path : str
        the main path of the workflow
    subjects_dir : str
        Freesurfer directory
    pipeline_name : str (default inv_sol_pipeline)
        name of the pipeline
    spacing : str (default 'ico-5')
        spacing to use to setup a source space
    inv_method : str (default MNE)
        the inverse method to use; possible choices: MNE, dSPM, sLORETA
    is_fixed : bool (default False)
        if True we use fixed orientation, otherwise the loose orientation
        is applied
    parc: str (default 'aparc')
        the parcellation defining the ROIs atlas in the source space
    aseg: bool (defualt False)
        if True a mixed source space will be created and the sub cortical
        regions defined in aseg_labels will be added to the source space
    aseg_labels: list (default [])
        list of substructures we want to include in the mixed source space
    noise_cov_fname: str (default None)
        template for the path to either the noise covariance matrix file or
        the empty room data
    all_src_space: bool
        if True we compute the inverse for all points of the source space
    ROIs_mean: bool
        if True we compute the mean of estimated time series on ROIs
    save_mixed_src_space: bool (defualt False)
        if True the mixed src space will be saved in the FS folder

    raw (inputnode): str
        path to raw data in fif format
    sbj_id (inputnode): str
        subject id

    Returns
    -------
    pipeline : instance of Workflow
    """

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    inputnode = pe.Node(IdentityInterface(fields=['sbj_id', 'raw',
                                                  'trans_file', 'cov_filename']),
                        name='inputnode')

    # Lead Field computation Node
    LF_computation = pe.Node(interface=LFComputation(), name='LF_computation')
    LF_computation.inputs.subjects_dir = subjects_dir
    LF_computation.inputs.spacing = spacing
    LF_computation.inputs.aseg = aseg
    if aseg:
        LF_computation.inputs.aseg_labels = aseg_labels
        LF_computation.inputs.save_mixed_src_space = save_mixed_src_space

    pipeline.connect(inputnode, 'sbj_id', LF_computation, 'sbj_id')
    pipeline.connect(inputnode, 'raw', LF_computation, 'raw_fname')
    pipeline.connect(inputnode, 'trans_file', LF_computation, 'trans_file')

    # Noise Covariance Matrix Node
    '''
    create_noise_cov = pe.Node(interface=NoiseCovariance(),
                               name="create_noise_cov")

    
    print('******************** {}', noise_cov_fname)
    create_noise_cov.inputs.cov_fname_in = noise_cov_fname
    create_noise_cov.inputs.is_epoched = True
    create_noise_cov.inputs.is_evoked = True
    
    pipeline.connect(inputnode, 'raw', create_noise_cov, 'raw_filename')
    '''
    # Inverse Solution Node
    inv_solution = pe.Node(interface=InverseSolution(), name='inv_solution')

    inv_solution.inputs.subjects_dir = subjects_dir
    inv_solution.inputs.inv_method = inv_method
    inv_solution.inputs.is_fixed = is_fixed
    inv_solution.inputs.is_ave = True
    inv_solution.inputs.snr = snr
    inv_solution.inputs.parc = parc
    inv_solution.inputs.aseg = aseg
    if aseg:
        inv_solution.inputs.aseg_labels = aseg_labels

    inv_solution.inputs.all_src_space = all_src_space
    inv_solution.inputs.ROIs_mean = ROIs_mean
    
    inv_solution.inputs.events_id = events_id
    inv_solution.inputs.condition = condition

    pipeline.connect(inputnode, 'sbj_id', inv_solution, 'sbj_id')

    pipeline.connect(inputnode, 'raw', inv_solution, 'raw_filename')
    pipeline.connect(LF_computation, 'fwd_filename',
                     inv_solution, 'fwd_filename')
    pipeline.connect(inputnode, 'cov_filename',
                     inv_solution, 'cov_filename')

    return pipeline
