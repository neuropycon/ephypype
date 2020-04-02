"Interface to MATLAB script"
import os

from nipype.interfaces.base import traits, TraitedSpec
from nipype.interfaces.matlab import MatlabCommand, MatlabInputSpec


class ReferenceInputSpec(MatlabInputSpec):
    data_file = traits.File(exists=True,
                            desc='FieldTrip data structure .mat',
                            mandatory=True)
    ft_path = traits.String('', desc='FieldTrip path', mandatory=True)
    channels = traits.String('', desc='channel names')
    updatesens = traits.String('', desc='update sensors (yes or no)', usedefault=True)  # noqa
    refmethod = traits.String('', desc='reference type (avg, bipolar)', mandatory=True)  # noqa


class ReferenceOutputSpec(TraitedSpec):
    matlab_output = traits.Str()
    data_output = traits.Str('', desc='data structure .mat')


class Reference(MatlabCommand):
    """
    Description:

    Apply the specified reference

    Inputs
    ------

    data_file : str
        data structure .mat (matlab format)

    ft_path : str
        path of FieldTrip package

    channels : str
        channels name to include in the reference process

    updatesens : bool
        update sensors information

    refmethod : str
        kind of reference (avg, bipolar)

    Outputs
    -------

    matlab_output : str
        file path of new FieldTrip data structure
    """
    input_spec = ReferenceInputSpec
    output_spec = ReferenceOutputSpec

    def _my_script(self):
        """This is where you implement your script"""
        script = """
        out_path = pwd
        out_file = fullfile(out_path, 'reref_grids')
        fpath = '%s'
        addpath(fpath)
        disp(fpath)
        ft_defaults
        load('%s');
        cfg             = [];
        cfg.channel     = %s;
        cfg.reref       = 'yes';
        cfg.refchannel  = 'all';
        cfg.refmethod   = '%s';
        reref_grids = ft_preprocessing(cfg, data);
        save(out_file, 'reref_grids')
        """ % (self.inputs.ft_path, self.inputs.data_file,
               self.inputs.channels, self.inputs.refmethod)
        return script

    def run(self, **inputs):
        # Inject your script
        self.data_output = os.path.abspath('reref_data.mat')
        self.inputs.script = self._my_script()
        results = super(MatlabCommand, self).run(**inputs)
        stdout = results.runtime.stdout
        # Attach stdout to outputs to access matlab results
        results.outputs.matlab_output = stdout
        print(stdout)
        return results

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['data_output'] = self.data_output
        return outputs
