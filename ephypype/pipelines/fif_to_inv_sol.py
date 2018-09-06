"""Inverse Solution Pipeline.

Author: Annalisa Pascarella <a.pascarella@iac.cnr.it>
"""

import nipype.pipeline.engine as pe

from nipype.interfaces.utility import IdentityInterface

from ephypype.preproc import get_raw_info, get_epochs_info
from ephypype.interfaces.mne.LF_computation import LFComputation
from ephypype.interfaces.mne.Inverse_solution import NoiseCovariance
from ephypype.interfaces.mne.Inverse_solution import InverseSolution


def create_pipeline_source_reconstruction(main_path, sbj_dir,
                                          pipeline_name='inv_sol_pipeline',
                                          spacing='ico-5',
                                          inv_method='MNE',
                                          is_epoched=False,
                                          events_id=None,
                                          t_min=None, t_max=None,
                                          is_evoked=False,
                                          parc='aparc',
                                          aseg=False,
                                          aseg_labels=[],
                                          noise_cov_fname=None,
                                          save_stc=False,
                                          save_mixed_src_space=False,
                                          is_fixed=False):
    """Source reconstruction pipeline.

    Parameters
    ----------
    main_path : str
        the main path of the workflow
    sbj_dir : str
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
        if True we use fixed orientation
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
    save_stc: bool (defualt False)
        if True the stc will be saved
    save_mixed_src_space: bool (defualt False)
        if True the mixed src space will be saved in the FS folder

    Inputs (inputnode)
    ------------------
    raw : str
        path to raw data in fif format
    sbj_id : str
        subject id

    Returns
    -------
    pipeline : instance of Workflow
    """
    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    inputnode = pe.Node(IdentityInterface(fields=['sbj_id', 'raw']),
                        name='inputnode')

    # Lead Field computation Node
    lf_computation = pe.Node(interface=LFComputation(), name='LF_computation')
    lf_computation.inputs.sbj_dir = sbj_dir
    lf_computation.inputs.spacing = spacing
    lf_computation.inputs.aseg = aseg
    if aseg:
        lf_computation.inputs.aseg_labels = aseg_labels
        lf_computation.inputs.save_mixed_src_space = save_mixed_src_space

    pipeline.connect(inputnode, 'sbj_id', lf_computation, 'sbj_id')

    try:
        events_id
    except NameError:
        events_id = None

    if is_epoched and events_id is None:
        pipeline.connect(inputnode, ('raw', get_epochs_info),
                         lf_computation, 'raw_info')
    else:
        pipeline.connect(inputnode, ('raw', get_raw_info),
                         lf_computation, 'raw_info')

    pipeline.connect(inputnode, 'raw', lf_computation, 'raw_fname')

    # Noise Covariance Matrix Node
    create_noise_cov = pe.Node(interface=NoiseCovariance(),
                               name="create_noise_cov")

#    if noise_cov_fname is not None:
    create_noise_cov.inputs.cov_fname_in = noise_cov_fname
    create_noise_cov.inputs.is_epoched = is_epoched
    create_noise_cov.inputs.is_evoked = is_evoked
    if is_evoked:
        create_noise_cov.inputs.events_id = events_id
        create_noise_cov.inputs.t_min = t_min
        create_noise_cov.inputs.t_max = t_max

    pipeline.connect(inputnode, 'raw', create_noise_cov, 'raw_filename')

    # Inverse Solution Node
    inv_solution = pe.Node(interface=InverseSolution(), name='inv_solution')

    inv_solution.inputs.sbj_dir = sbj_dir
    inv_solution.inputs.inv_method = inv_method
    inv_solution.inputs.is_epoched = is_epoched
    inv_solution.inputs.is_fixed = is_fixed

    if is_epoched and events_id is not None:
        inv_solution.inputs.events_id = events_id
        inv_solution.inputs.t_min = t_min
        inv_solution.inputs.t_max = t_max

    inv_solution.inputs.is_evoked = is_evoked
    if is_epoched and is_evoked:
        inv_solution.inputs.events_id = events_id

    inv_solution.inputs.parc = parc
    inv_solution.inputs.aseg = aseg
    if aseg:
        inv_solution.inputs.aseg_labels = aseg_labels

    inv_solution.inputs.save_stc = save_stc

    pipeline.connect(inputnode, 'sbj_id', inv_solution, 'sbj_id')
    pipeline.connect(inputnode, 'raw', inv_solution, 'raw_filename')
    pipeline.connect(lf_computation, 'fwd_filename',
                     inv_solution, 'fwd_filename')
    pipeline.connect(create_noise_cov, 'cov_fname_out',
                     inv_solution, 'cov_filename')

    return pipeline
