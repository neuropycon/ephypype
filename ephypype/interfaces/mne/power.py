"""Power computation module."""

# Authors: Dmitrii Altukhov <daltuhov@hse>
#          Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)


from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec
from ...power import _compute_and_save_psd, _compute_and_save_src_psd


class PowerInputSpec(BaseInterfaceInputSpec):
    """Power input spec."""

    data_file = traits.File(exists=True,
                            desc='File with mne.Epochs or mne.io.Raw or .npy',
                            mandatory=True)
    inv_file = traits.File(exists=True,
                           desc='File with inverse operator',
                           mandatory=False)

    inv_method = traits.String('MNE', desc='possible inverse methods are \
                               sLORETA, MNE, dSPM', usedefault=True,
                               mandatory=True)

    fmin = traits.Float(desc='lower psd frequency', mandatory=False)
    fmax = traits.Float(desc='higher psd frequency', mandatory=False)

    sfreq = traits.Float(desc='sampling frequency', mandatory=False)

    nfft = traits.Int(256, desc='the length of FFT used', usedefault=True,
                      mandatory=False)
    overlap = traits.Float(0, desc='Number of points of overlap btw segments',
                           usedefault=True, mandatory=False)
    method = traits.Enum('welch', 'multitaper',
                         desc='power spectral density computation method')
    is_epoched = traits.Bool(desc='if true input data are mne.Epochs',
                             mandatory=False)
    is_sensor_space = traits.Bool(True, usedefault=True,
                                  dedesc='True for PSD on sensor space \
                                  False for PSD on source',
                                  mandatory=False)
    snr = traits.Float(3.0, usedefault=True, desc='use smaller SNR for \
                       raw data', mandatory=False)


class PowerOutputSpec(TraitedSpec):
    """Power output spec."""

    psds_file = File(exists=True,
                     desc='psd tensor and frequencies in .npz format')


class Power(BaseInterface):
    """Compute power spectral density on epochs or raw data.

    Inputs
    ------
        data_file : str
            Filename of the data
        fmin : float
            Lower psd frequency
        fmax : float
            Higher psd frequency
        sfreq : float
            Sampling frequency
        nfft : int
            The length of FFT used
        overlap : float
            Number of points of overlap between segments
        method : str
            Power spectral density computation method. Possible values are
            'welch', 'multitaper'
        is_epoched : bool
            If true input data are mne.Epochs
        is_sensor_space : bool
            True for PSD on sensor space, False for PSD on source

    Outputs
    -------
        psds_file : str
            Name of the .npz file containing psd tensor and frequencies
    """

    input_spec = PowerInputSpec
    output_spec = PowerOutputSpec

    def _run_interface(self, runtime):
        data_file = self.inputs.data_file
        inv_file = self.inputs.inv_file
        inv_method = self.inputs.inv_method
        sfreq = self.inputs.sfreq
        snr = self.inputs.snr
        fmin = self.inputs.fmin
        fmax = self.inputs.fmax
        nfft = self.inputs.nfft
        overlap = self.inputs.overlap
        method = self.inputs.method
        is_epoched = self.inputs.is_epoched
        is_sensor_space = self.inputs.is_sensor_space
        if is_sensor_space:
            self.psds_file = _compute_and_save_psd(data_file, fmin, fmax,
                                                   method, is_epoched)
        else:
            self.psds_file = _compute_and_save_src_psd(data_file, sfreq, inv_file,
                                                       fmin=fmin, fmax=fmax,
                                                       n_fft=nfft, snr=snr,
                                                       n_overlap=overlap,
                                                       is_epoched=is_epoched,
                                                       inv_method=inv_method)
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['psds_file'] = self.psds_file
        return outputs
