"""MNE inverse solution."""
# Created on Mon May  2 17:24:00 2016
# @author: pasca

import os.path as op
import sys
import glob

from nipype.utils.filemanip import split_filename as split_f

from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec
from nipype.interfaces.base import traits, File, TraitedSpec

from ephypype.compute_inv_problem import compute_inverse_solution
from ephypype.preproc import create_reject_dict
from mne import find_events, compute_raw_covariance, compute_covariance
from mne import pick_types, write_cov, Epochs
from mne.io import read_raw_fif, read_raw_ctf


class InverseSolutionConnInputSpec(BaseInterfaceInputSpec):
    """Inverse slution conn input spec."""

    sbj_id = traits.String(desc='subject id', mandatory=True)

    sbj_dir = traits.Directory(exists=True, desc='Freesurfer main directory',
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

    events_id = traits.Dict(None, desc='the id of all events to consider.',
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
    """Inverse solution conn output spec."""

    ts_file = File(exists=False, desc='source reconstruction in .npy format')
    labels = File(exists=False, desc='labels file in pickle format')
    label_names = File(exists=False, desc='labels name file in txt format')
    label_coords = File(exists=False, desc='labels coords file in txt format')


class InverseSolution(BaseInterface):
    """Compute the inverse solution on raw or epoch data.

    This class is considering N_r regions in source space based on a FreeSurfer
    cortical parcellation.

    Parameters
    ----------
        sbj_id : str
            subject name
        sbj_dir : str
            Freesurfer directory
        raw_filename : str
            filename of the raw data
        cov_filename : str
            filename of the noise covariance matrix
        fwd_filename : str
            filename of the forward operator
        is_epoched : bool
            if True and events_id = None the input data are epoch data
            in the format -epo.fif
            if True and events_id is not None, the raw data are epoched
            according to events_id and t_min and t_max values
        events_id: dict
            the dict of events
        t_min, t_max: int (defualt None)
            define the time interval in which to epoch the raw data
        is_evoked: bool
            if True the raw data will be averaged according to the events
            contained in the dict events_id
        is_fixed : bool
            if True we use fixed orientation
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
    """

    input_spec = InverseSolutionConnInputSpec
    output_spec = InverseSolutionConnOutputSpec

    def _run_interface(self, runtime):

        sbj_id = self.inputs.sbj_id
        sbj_dir = self.inputs.sbj_dir
        raw_filename = self.inputs.raw_filename
        cov_filename = self.inputs.cov_filename
        fwd_filename = self.inputs.fwd_filename
        is_epoched = self.inputs.is_epoched
        is_fixed = self.inputs.is_fixed
        events_id = self.inputs.events_id
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

        self.ts_file, self.labels, self.label_names, self.label_coords = \
            compute_inverse_solution(raw_filename, sbj_id, sbj_dir,
                                     fwd_filename, cov_filename,
                                     is_epoched, events_id,
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

        return outputs


class NoiseCovarianceConnInputSpec(BaseInterfaceInputSpec):
    """Noise covariance conn input spec."""

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
    """Noise covariance conn output spec."""

    cov_fname_out = File(exists=False, desc='Noise covariances matrix')


class NoiseCovariance(BaseInterface):
    """Compute the noise covariance matrix.

    Parameters
    ----------
    raw_filename : str
        filename of the raw data
    cov_fname_in : str
        filename of the noise covariance matrix
    is_epoched : bool
        True if we want to epoch the data
    is_evoked : bool
        True if we want to analyze evoked data
    events_id : dict
        the id of all events to consider
    t_min : float
        start time before event
    tmax : float
        end time after event
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

        if not op.isfile(cov_fname_in):
            if is_epoched and is_evoked:
                raw = read_raw_fif(raw_filename)
                events = find_events(raw)

                if not op.isfile(self.cov_fname_out):
                    print(('\n*** COMPUTE COV FROM EPOCHS ***\n' +
                           self.cov_fname_out))

                    reject = create_reject_dict(raw.info)
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
                '\n *** RAW DATA \n'
                for er_fname in glob.glob(op.join(data_path, cov_fname_in)):
                    print(('\n found file name %s  \n' % er_fname))

                try:
                    if er_fname.rfind('cov.fif') > -1:
                        print("\n *** NOISE cov file %s exists!! "
                              "\n" % er_fname)
                        self.cov_fname_out = er_fname
                    else:
                        if er_fname.rfind('.fif') > -1:
                            er_raw = read_raw_fif(er_fname)
                            er_fname = er_fname.replace('.fif', '-raw-cov.fif')
                        elif er_fname.rfind('.ds') > -1:
                            er_raw = read_raw_ctf(er_fname)
                            er_fname = er_fname.replace('.ds', '-raw-cov.fif')

                        self.cov_fname_out = op.join(data_path, er_fname)

                        if not op.isfile(self.cov_fname_out):
                            reject = create_reject_dict(er_raw.info)
                            picks = pick_types(er_raw.info, meg=True,
                                               ref_meg=False, exclude='bads')

                            noise_cov = compute_raw_covariance(er_raw,
                                                               picks=picks,
                                                               reject=reject)
                            write_cov(self.cov_fname_out, noise_cov)
                        else:
                            print(('\n *** NOISE cov file %s exists!!! \n'
                                   % self.cov_fname_out))
                except NameError:
                    sys.exit("No covariance matrix as input!")
                    # TODO creare una matrice diagonale?

        else:
            print(('\n *** NOISE cov file %s exists!!! \n' % cov_fname_in))
            self.cov_fname_out = cov_fname_in

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['cov_fname_out'] = self.cov_fname_out

        return outputs
