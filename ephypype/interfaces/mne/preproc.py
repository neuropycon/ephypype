"""Interfaces for preprocessing nodes."""

# Authors: Dmitrii Altukhov <daltuhov@hse>
#
# License: BSD (3-clause)


from nipype.interfaces.base import BaseInterface,\
    BaseInterfaceInputSpec, traits, TraitedSpec

from ...preproc import _compute_ica,\
    _preprocess_fif,\
    _create_epochs, _define_epochs


class CompIcaInputSpec(BaseInterfaceInputSpec):
    """Input specification for CompIca."""

    fif_file = traits.File(exists=True,
                           desc='filtered raw meg data in fif format',
                           mandatory=True)
    raw_fif_file = traits.File(exists=True,
                               desc='orignal raw meg data in fif format',
                               mandatory=True)
    ecg_ch_name = traits.String(desc='name of ecg channel')
    eog_ch_name = traits.String(desc='name of eog channel')
    n_components = traits.Float(desc='number of ica components')
    reject = traits.Dict(desc='rejection parameters', mandatory=False)


class CompIcaOutputSpec(TraitedSpec):
    """Output specification for CompIca."""

    ica_file = traits.File(exists=True,
                           desc='file with raw file in .fif',
                           mandatory=True)

    ica_sol_file = traits.File(exists=True,
                               desc='file with ica solution in .fif',
                               mandatory=True)
    ica_ts_file = traits.File(exists=True,
                              desc='file with ica components in .fif',
                              mandatory=True)

    report_file = traits.File(exists=True,
                              desc='ica report in .html',
                              mandatory=True)


class CompIca(BaseInterface):
    """Compute ICA solution on raw fif data.

    Inputs
    ------
    fif_file : str
        Filename of raw meg data in fif format
    ecg_ch_name : str
        Name of ecg channel
    eog_ch_name : str
        Name of eog channel
    n_components : float
        Number of ica components
    reject : dict
        Rejection parameters

    Outputs
    -------
    ica_file : str
        Name of .fif file with raw data
    ica_sol_file : str
        Name of .fif file with ica solution
    ica_ts_file : str
        Name of .fif file with ica components
    report_file : str
        Name of html file with ica report
    """

    input_spec = CompIcaInputSpec
    output_spec = CompIcaOutputSpec

    def _run_interface(self, runtime):
        raw_fif_file = self.inputs.raw_fif_file
        fif_file = self.inputs.fif_file
        ecg_ch_name = self.inputs.ecg_ch_name
        eog_ch_name = self.inputs.eog_ch_name
        n_components = self.inputs.n_components
        reject = self.inputs.reject

        if reject == traits.Undefined:
            reject = dict(mag=4e-12, grad=4000e-13)

        ica_output = _compute_ica(fif_file, raw_fif_file, ecg_ch_name,
                                  eog_ch_name, n_components, reject)
        self.ica_file = ica_output[0]
        self.ica_sol_file = ica_output[1]
        self.ica_ts_file = ica_output[2]
        self.report_file = ica_output[3]

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['ica_file'] = self.ica_file
        outputs['ica_sol_file'] = self.ica_sol_file
        outputs['ica_ts_file'] = self.ica_ts_file
        outputs['report_file'] = self.report_file
        return outputs


class PreprocFifInputSpec(BaseInterfaceInputSpec):
    """Input specification for PreprocFif."""

    fif_file = traits.File(exists=True,
                           desc='raw meg data in fif format',
                           mandatory=True)
    l_freq = traits.Float(desc='lower bound for filtering')
    h_freq = traits.Float(desc='upper bound for filtering')
    down_sfreq = traits.Int(None, desc='downsampling frequency',
                            mandatory=False)


class PreprocFifOutputSpec(TraitedSpec):
    """Output specification for PreprocFif."""

    fif_file = traits.File(exists=True,
                           desc='.fif file',
                           mandatory=True)


class PreprocFif(BaseInterface):
    """Interface for preproc.preprocess_fif.

    Inputs
    ------
    fif_file : str
        Filename of raw meg data in fif format
    l_freq : float
        Llower bound for filtering
    h_freq : float
        Upper bound for filtering
    down_sfreq : int
        Downsampling frequency

    Outputs
    -------
    fif_file : str
        Name of .fif file with preprocessed raw data
    """

    input_spec = PreprocFifInputSpec
    output_spec = PreprocFifOutputSpec

    def _run_interface(self, runtime):
        fif_file = self.inputs.fif_file
        l_freq = self.inputs.l_freq
        h_freq = self.inputs.h_freq
        down_sfreq = self.inputs.down_sfreq

        result_fif = _preprocess_fif(fif_file, l_freq, h_freq, down_sfreq)

        self.fif_file = result_fif
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['fif_file'] = self.fif_file
        return outputs


class CreateEpInputSpec(BaseInterfaceInputSpec):
    """Input specification for CreateEp."""

    fif_file = traits.File(exists=True,
                           desc='raw meg data in fif format',
                           mandatory=True)
    ep_length = traits.Float(desc='epoch length in seconds')


class CreateEpOutputSpec(TraitedSpec):
    """Output specification for CreateEp."""

    epo_fif_file = traits.File(exists=True,
                               desc='-epo.fif file',
                               mandatory=True)


class CreateEp(BaseInterface):
    """Interface for preproc.create_epochs.

    Inputs
    ------
    fif_file : str
        Filename of raw meg data in fif format
    ep_length : str
        Epoch length in seconds

    Outputs
    -------
    epo_fif_file : str
        Name of .fif file with epoched data
    """

    input_spec = CreateEpInputSpec
    output_spec = CreateEpOutputSpec

    def _run_interface(self, runtime):
        fif_file = self.inputs.fif_file
        ep_length = self.inputs.ep_length

        result_fif = _create_epochs(fif_file, ep_length)

        self.epo_fif_file = result_fif
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['epo_fif_file'] = self.epo_fif_file
        return outputs


class DefineEpochsInputSpec(BaseInterfaceInputSpec):
    """Input specification for DefineEpochs."""

    fif_file = traits.File(exists=True,
                           desc='raw meg data in fif format',
                           mandatory=True)
    events_id = traits.Dict(None, desc='the id of all events to consider.',
                            mandatory=False)
    events_file = traits.String('', exists=True, desc='events filename',
                                mandatory=False)
    t_min = traits.Float(None, desc='start time before event', mandatory=False)
    t_max = traits.Float(None, desc='end time after event', mandatory=False)
    decim = traits.Int(1, desc='Factor by which to downsample the data',
                       mandatory=False, usedefault=True)


class DefineEpochsOutputSpec(TraitedSpec):
    """Output specification for DefineEpochs."""

    epo_fif_file = traits.File(exists=True,
                               desc='-epo.fif file',
                               mandatory=True)


class DefineEpochs(BaseInterface):
    """Interface for preproc.create_epochs.

    Inputs
    ------
    fif_file : str
        Filename of raw meg data in fif format
    ep_length : str
        Epoch length in seconds

    Outputs
    -------
    epo_fif_file : str
        Name of .fif file with epoched data
    """

    input_spec = DefineEpochsInputSpec
    output_spec = DefineEpochsOutputSpec

    def _run_interface(self, runtime):
        fif_file = self.inputs.fif_file
        events_id = self.inputs.events_id
        events_file = self.inputs.events_file
        t_min = self.inputs.t_min
        t_max = self.inputs.t_max
        decim = self.inputs.decim
        result_fif = _define_epochs(fif_file, t_min, t_max, events_id,
                                    events_file, decim)

        self.epo_fif_file = result_fif
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['epo_fif_file'] = self.epo_fif_file
        return outputs
