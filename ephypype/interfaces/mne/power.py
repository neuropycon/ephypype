"""
Power computation module
"""
# Author: Dmitrii Altukhov <dm-altukhov@ya.ru>

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from ephypype.power import compute_and_save_psd, compute_and_save_src_psd


class PowerInputSpec(BaseInterfaceInputSpec):
    data_file = traits.File(exists=True,
                            desc='File with mne.Epochs or mne.io.Raw or .npy',
                            mandatory=True)

    fmin = traits.Float(desc='lower psd frequency', mandatory=False)
    fmax = traits.Float(desc='higher psd frequency', mandatory=False)

    sfreq = traits.Float(desc='sampling frequency', mandatory=False)

    nfft = traits.Int(desc='the length of FFT used', mandatory=False)
    overlap = traits.Float(desc='The number of points of overlap between segments',
                           mandatory=False)

    method = traits.Enum('welch', 'multitaper',
                         desc='power spectral density computation method')

    is_epoched = traits.Bool(desc='if true input data are mne.Epochs',
                             mandatory=False)

    is_sensor_space = traits.Bool(True, usedefault=True,
                                  dedesc='True for PSD on sensor space \
                                  False for PSD on source',
                                  mandatory=False)


class PowerOutputSpec(TraitedSpec):
    psds_file = File(exists=True,
                     desc='psd tensor and frequencies in .npz format')


class Power(BaseInterface):
    """
    Compute power spectral density on epochs or raw data
    """
    input_spec = PowerInputSpec
    output_spec = PowerOutputSpec

    def _run_interface(self, runtime):
        print('in Power')
        data_file = self.inputs.data_file
        sfreq = self.inputs.sfreq
        fmin = self.inputs.fmin
        fmax = self.inputs.fmax
        nfft = self.inputs.nfft
        overlap = self.inputs.overlap
        method = self.inputs.method
        is_epoched = self.inputs.is_epoched
        is_sensor_space = self.inputs.is_sensor_space

        if is_sensor_space:
            self.psds_file = compute_and_save_psd(data_file, fmin, fmax,
                                                  method, is_epoched)
        else:
            self.psds_file = compute_and_save_src_psd(data_file, sfreq,
                                                      fmin=fmin, fmax=fmax,
                                                      n_fft=nfft,
                                                      n_overlap=overlap,
                                                      is_epoched=is_epoched)
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['psds_file'] = self.psds_file
        return outputs
