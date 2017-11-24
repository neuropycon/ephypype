"""
Power computation module
"""
# Author: Dmitrii Altukhov <dm-altukhov@ya.ru>

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from ephypype.power import compute_and_save_psd


class PowerInputSpec(BaseInterfaceInputSpec):
    data_file = traits.File(exists=True,
                            desc='File with mne.Epochs or mne.io.Raw',
                            mandatory=True)
    fmin = traits.Float(desc='lower psd frequency', mandatory=False)
    fmax = traits.Float(desc='higher psd frequency', mandatory=False)
    method = traits.Enum('welch', 'multitaper',
                         desc='power spectral density computation method')
    is_epoched = traits.Bool(desc='if true input data are mne.Epochs',
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
        fmin = self.inputs.fmin
        fmax = self.inputs.fmax
        method = self.inputs.method
        is_epoched = self.inputs.is_epoched
        self.psds_file = compute_and_save_psd(data_file, fmin, fmax, method,
                                              is_epoched)
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['psds_file'] = self.psds_file
        return outputs
