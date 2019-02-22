"""Inverse problem Interfaces."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import os.path as op

from nipype.utils.filemanip import split_filename as split_f

from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec
from nipype.interfaces.base import traits, File, TraitedSpec

from ...compute_inv_problem import _compute_inverse_solution, compute_noise_cov
from ...preproc import _create_reject_dict
from mne import find_events, compute_covariance
from mne import pick_types, write_cov, Epochs
from mne.io import read_raw_fif


class InverseSolutionConnInputSpec(BaseInterfaceInputSpec):
    """Input specification for InverseSolution."""

    sbj_id = traits.String(desc='subject id', mandatory=True)
    subjects_dir = traits.Directory(exists=True, desc='Freesurfer main directory',  # noqa
                                    mandatory=True)
    raw_filename = traits.File(exists=True, desc='raw filename',
                               mandatory=True)
    cov_filename = traits.File(exists=True, desc='Noise Covariance matrix',
                               mandatory=True)
    fwd_filename = traits.File(exists=True, desc='LF matrix', mandatory=True)
    is_epoched = traits.Bool(False, usedefault=True,
                             desc='if true raw data will be epoched',
                             mandatory=False)
    is_fixed = traits.Bool(False, usedefault=True,
                           desc='if true we use fixed orientation',
                           mandatory=False)
    events_id = traits.Dict({}, desc='the id of all events to consider.',
                            usedefault=True, mandatory=False)
    events_file = traits.File(None, exists=True, desc='events filename',
                              mandatory=False)
    t_min = traits.Float(None, desc='start time before event', mandatory=False)
    t_max = traits.Float(None, desc='end time after event', mandatory=False)
    is_evoked = traits.Bool(desc='if true if we want to analyze evoked data',
                            mandatory=False)
    inv_method = traits.String('MNE', desc='possible inverse methods are \
                               sLORETA, MNE, dSPM', usedefault=True,
                               mandatory=True)
    snr = traits.Float(1.0, usedefault=True, desc='use smaller SNR for \
                       raw data', mandatory=False)
    parc = traits.String('aparc', usedefault=True,
                         desc='the parcellation to use: aparc vs aparc.a2009s',
                         mandatory=False)
    aseg = traits.Bool(desc='if true sub structures will be considered',
                       mandatory=False)
    aseg_labels = traits.List(desc='list of substructures in the src space',
                              mandatory=False)
    all_src_space = traits.Bool(False, desc='if true compute inverse on all \
                                source space', usedefault=True,
                                mandatory=False)
    ROIs_mean = traits.Bool(True, desc='if true compute mean on ROIs',
                            usedefault=True, mandatory=False)


class InverseSolutionConnOutputSpec(TraitedSpec):
    """Output specification for InverseSolution."""

    ts_file = File(exists=False, desc='source reconstruction in .npy format')
    labels = File(exists=False, desc='labels file in pickle format')
    label_names = File(exists=False, desc='labels name file in txt format')
    label_coords = File(exists=False, desc='labels coords file in txt format')
    good_events_file = File(exists=False, desc='good events filename')


class InverseSolution(BaseInterface):
    """Compute the inverse solution on raw or epoch data.

    This class is considering N_r regions in source space based on a FreeSurfer
    cortical parcellation.

    Inputs
    ------
        sbj_id : str
            Subject name
        subjects_dir : str
            Freesurfer directory
        raw_filename : str
            Filename of the raw data
        cov_filename : str
            Filename of the noise covariance matrix
        fwd_filename : str
            Filename of the forward operator
        is_epoched : bool
            If True and events_id = None the input data are epoch data
            in the format -epo.fif
            if True and events_id is not None, the raw data are epoched
            according to events_id and t_min and t_max values
        events_id: dict
            The dict of events
        t_min, t_max: int (defualt None)
            Define the time interval in which to epoch the raw data
        is_evoked: bool
            If True the raw data will be averaged according to the events
            contained in the dict events_id
        is_fixed : bool
            If True we use fixed orientation
        inv_method : str
            The inverse method to use; possible choices: MNE, dSPM, sLORETA
        snr : float
            The SNR value used to define the regularization parameter
        parc: str
            The parcellation defining the ROIs atlas in the source space
        aseg: bool
            If True a mixed source space will be created and the sub cortical
            regions defined in aseg_labels will be added to the source space
        aseg_labels: list
            List of substructures we want to include in the mixed source space
        all_src_space: bool
            If True we compute the inverse for all points of the s0urce space
        ROIs_mean: bool
            If True we compute the mean of estimated time series on ROIs

    Outputs
    -------
        ts_file : str
            Name of the .npy file with the estimated source time series
        labels : str
            Labels file in pickle format
        label_names : str
            Name of the .txt file with labels name
        label_coords : str
            Name of the .txt file with labels coordinates

    """

    input_spec = InverseSolutionConnInputSpec
    output_spec = InverseSolutionConnOutputSpec

    def _run_interface(self, runtime):

        sbj_id = self.inputs.sbj_id
        subjects_dir = self.inputs.subjects_dir
        raw_filename = self.inputs.raw_filename
        cov_filename = self.inputs.cov_filename
        fwd_filename = self.inputs.fwd_filename
        is_epoched = self.inputs.is_epoched
        is_fixed = self.inputs.is_fixed
        events_id = self.inputs.events_id
        events_file = self.inputs.events_file
        t_min = self.inputs.t_min
        t_max = self.inputs.t_max
        is_evoked = self.inputs.is_evoked
        inv_method = self.inputs.inv_method
        snr = self.inputs.snr
        parc = self.inputs.parc
        aseg = self.inputs.aseg
        aseg_labels = self.inputs.aseg_labels
        all_src_space = self.inputs.all_src_space
        ROIs_mean = self.inputs.ROIs_mean

        self.ts_file, self.labels, self.label_names, \
            self.label_coords, self.good_events_file = \
            _compute_inverse_solution(raw_filename, sbj_id, subjects_dir,
                                      fwd_filename, cov_filename,
                                      is_epoched, events_id, events_file,
                                      t_min, t_max, is_evoked,
                                      snr, inv_method, parc,
                                      aseg, aseg_labels, all_src_space,
                                      ROIs_mean, is_fixed)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['ts_file'] = self.ts_file
        outputs['labels'] = self.labels
        outputs['label_names'] = self.label_names
        outputs['label_coords'] = self.label_coords
        outputs['good_events_file'] = self.good_events_file

        return outputs


class NoiseCovarianceConnInputSpec(BaseInterfaceInputSpec):
    """Input specification for NoiseCovariance."""

    cov_fname_in = traits.File(exists=False, desc='file name for Noise \
                               Covariance Matrix')
    raw_filename = traits.File(exists=True, desc='raw data filename')
    is_epoched = traits.Bool(desc='true if we want to epoch the data',
                             mandatory=False)
    is_evoked = traits.Bool(desc='true if we want to analyze evoked data',
                            mandatory=False)
    events_id = traits.Dict(None, desc='the id of all events to consider.',
                            mandatory=False)
    t_min = traits.Float(None, desc='start time before event', mandatory=False)
    t_max = traits.Float(None, desc='end time after event', mandatory=False)


class NoiseCovarianceConnOutputSpec(TraitedSpec):
    """Output specification for NoiseCovariance."""

    cov_fname_out = File(exists=False, desc='Noise covariances matrix')


class NoiseCovariance(BaseInterface):
    """Compute the noise covariance matrix.

    Inputs
    ------
    raw_filename : str
        Filename of the raw data
    cov_fname_in : str
        Filename of the noise covariance matrix
    is_epoched : bool
        True if we want to epoch the data
    is_evoked : bool
        True if we want to analyze evoked data
    events_id : dict
        The id of all events to consider
    t_min : float
        start time before event
    tmax : float
        End time after event

    Outputs
    -------
       cov_fname_out : str
           Filename of the noise covariance matrix
    """

    input_spec = NoiseCovarianceConnInputSpec
    output_spec = NoiseCovarianceConnOutputSpec

    def _run_interface(self, runtime):

        raw_filename = self.inputs.raw_filename
        cov_fname_in = self.inputs.cov_fname_in
        is_epoched = self.inputs.is_epoched
        is_evoked = self.inputs.is_evoked
        events_id = self.inputs.events_id
        t_min = self.inputs.t_min
        t_max = self.inputs.t_max

        data_path, basename, ext = split_f(raw_filename)

        self.cov_fname_out = op.join(data_path, '%s-cov.fif' % basename)

        # Check if a noise cov matrix was already computed
        if not op.isfile(cov_fname_in):
            if is_epoched and is_evoked:
                raw = read_raw_fif(raw_filename)
                events = find_events(raw)

                if not op.isfile(self.cov_fname_out):
                    print(('\n*** COMPUTE COV FROM EPOCHS ***\n' +
                           self.cov_fname_out))

                    reject = _create_reject_dict(raw.info)
                    picks = pick_types(raw.info, meg=True, ref_meg=False,
                                       exclude='bads')

                    epochs = Epochs(raw, events, events_id, t_min, t_max,
                                    picks=picks, baseline=(None, 0),
                                    reject=reject)

                    # TODO method='auto'? too long!!!
                    noise_cov = compute_covariance(epochs, tmax=0,
                                                   method='diagonal_fixed')
                    write_cov(self.cov_fname_out, noise_cov)
                else:
                    print(('\n *** NOISE cov file %s exists!!! \n'
                           % self.cov_fname_out))
            else:
                # Compute noise cov matrix from empty room data
                self.cov_fname_out = compute_noise_cov(
                    op.join(data_path, cov_fname_in), raw_filename)

        else:
            print(('\n *** NOISE cov file {} exists!!! \n'.
                   format(cov_fname_in)))
            self.cov_fname_out = cov_fname_in

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['cov_fname_out'] = self.cov_fname_out

        return outputs
