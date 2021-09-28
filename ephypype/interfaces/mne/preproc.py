"""Interfaces for preprocessing nodes."""

# Authors: Dmitrii Altukhov <daltuhov@hse>
#
# License: BSD (3-clause)


from nipype.interfaces.base import BaseInterface,\
    BaseInterfaceInputSpec, traits, TraitedSpec

from ...preproc import _compute_ica,\
    _preprocess_fif,\
    _create_epochs, _define_epochs, _compute_evoked


class CompIcaInputSpec(BaseInterfaceInputSpec):
    """Input specification for CompIca."""

    fif_file = traits.File(exists=True,
                           desc='filtered raw meg data in fif format',
                           mandatory=True)
    raw_fif_file = traits.File(exists=True,
                               desc='orignal raw meg data in fif format',
                               mandatory=True)
    ecg_ch_name = traits.String(desc='name of ecg channel')
    eog_ch_name = traits.List(desc='name of eog channel')
    data_type = traits.String(desc='data type (MEG or EEG)')
    n_components = traits.Int(desc='number of ica components')
    variance = traits.Float(desc='number of ica components')
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
    variance : float
        Number of ica components
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
        variance = self.inputs.variance
        reject = self.inputs.reject
        data_type = self.inputs.data_type

        if reject == traits.Undefined:
            reject = dict(mag=4e-12, grad=4000e-13)

        n_components = variance if variance else n_components
        ica_output = _compute_ica(
            fif_file, raw_fif_file, data_type, ecg_ch_name,
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
    h_freq = traits.Float(
        None, desc='upper bound for filtering', mandatory=False)
    data_type = traits.String('fif', desc='data type', usedefault=True)
    montage = traits.String(desc='EEG layout')
    misc = traits.String(desc='EEG misc channels')
    bipolar = traits.Dict(desc='set EEG bipolar channels')
    ch_new_names = traits.Dict(desc='new channel name')
    eog = traits.List(desc='EEG eog channels')
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
    data_type : str
        Data type (.fif, .set)
    montage : str
        EEG montage
    misc : str
        miscellaneous channles
    bipolar : dict
        EEG bipolar channels
    ch_new_names : dict
        rename channels
    eog : list
        eog channel names

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
        data_type = self.inputs.data_type

        if data_type == 'eeg':
            montage = self.inputs.montage
            misc = self.inputs.misc
            bipolar = self.inputs.bipolar
            EoG_ch_name = self.inputs.eog
            ch_new_names = self.inputs.ch_new_names
        else:
            montage, misc, bipolar, EoG_ch_name = None, None, None, None
            ch_new_names = None

        result_fif = _preprocess_fif(
            fif_file, data_type, l_freq=l_freq, h_freq=h_freq,
            down_sfreq=down_sfreq, montage=montage, misc=misc,
            eog_ch=EoG_ch_name, bipolar=bipolar, ch_new_names=ch_new_names)

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
    data_type = traits.String('meg', exists=True, desc='data type',
                              mandatory=False, usedefault=True)
    baseline = traits.Tuple((None, 0), desc='baseline', mandatory=False,
                            usedefault=True)


class DefineEpochsOutputSpec(TraitedSpec):
    """Output specification for DefineEpochs."""

    epo_fif_file = traits.File(exists=True,
                               desc='-epo.fif file',
                               mandatory=True)


class DefineEpochs(BaseInterface):
    """Interface for preproc.define_epochs.

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
        data_type = self.inputs.data_type
        baseline = self.inputs.baseline

        result_fif = _define_epochs(fif_file, t_min, t_max, events_id,
                                    events_file=events_file, decim=decim,
                                    data_type=data_type, baseline=baseline)
        self.epo_fif_file = result_fif
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['epo_fif_file'] = self.epo_fif_file
        return outputs


class DefineEvokedInputSpec(BaseInterfaceInputSpec):
    """Input specification for DefineEpochs."""

    fif_file = traits.File(exists=True,
                           desc='epoched data in fif format',
                           mandatory=True)
    events_id = traits.Dict(None, desc='the id of all events to consider.',
                            mandatory=False)
    condition = traits.List(None, desc='conditions to consider.',
                            mandatory=False)


class DefineEvokedOutputSpec(TraitedSpec):
    """Output specification for DefineEpochs."""

    evo_fif_file = traits.File(exists=True,
                               desc='-ave.fif file',
                               mandatory=True)


class DefineEvoked(BaseInterface):
    """Interface for preproc._compute_evoked

    Inputs
    ------
    fif_file : str
        Filename of epoched data in fif format
    events_id : dict
        events id
    condition : dict
        condition for averaging

    Outputs
    -------
    evo_fif_file : str
        Name of .fif file with evoked data
    """

    input_spec = DefineEvokedInputSpec
    output_spec = DefineEvokedOutputSpec

    def _run_interface(self, runtime):
        fif_file = self.inputs.fif_file
        events_id = self.inputs.events_id
        condition = self.inputs.condition

        result_fif = _compute_evoked(fif_file, events_id, condition)

        self.evo_fif_file = result_fif
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['evo_fif_file'] = self.evo_fif_file
        return outputs
