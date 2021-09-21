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
#    updatesens = traits.String('', desc='update sensors (yes or no)', usedefault=True)  # noqa
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

    data_output : str
        fieldtrip data structure in .mat containing the rereferce data
    """
    input_spec = ReferenceInputSpec
    output_spec = ReferenceOutputSpec

    def _avg_reference(self):
        """call FieldTrip function to Re-montage the cortical grids to a
        common average reference """
        script = """
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
        reref_data = ft_preprocessing(cfg, data);
        save('%s', 'reref_data')
        """ % (self.inputs.ft_path, self.inputs.data_file,
               self.inputs.channels, self.inputs.refmethod, self.data_output)
        return script

    def _bipolar_reference(self):
        """call FieldTrip function to Apply a bipolar montage to the depth
        electrodes"""
        script = """
        fpath = '%s'
        addpath(fpath)
        disp(fpath)
        ft_defaults
        load('%s');
        depths = %s;
        for d = 1:numel(depths)
            cfg             = [];
            cfg.channel     = ft_channelselection(depths{d}, data.label);
            cfg.reref       = 'yes';
            cfg.refchannel  = 'all';
            cfg.refmethod   = '%s';
            cfg.updatesens  = 'yes';
            reref_depths{d} = ft_preprocessing(cfg, data);
        end
        cfg            = [];
        cfg.appendsens = 'yes';
        reref_data = ft_appenddata(cfg, reref_depths{:});
        save('%s', 'reref_data')
        """ % (self.inputs.ft_path, self.inputs.data_file,
               self.inputs.channels, self.inputs.refmethod, self.data_output)
        return script

    def run(self, **inputs):
        # Inject your script
        self.data_output = os.path.abspath('reref_data.mat')
        if self.inputs.refmethod == 'avg':
            print('*** APPLY {} reference'.format(self.inputs.refmethod))
            self.inputs.script = self._avg_reference()
        elif self.inputs.refmethod == 'bipolar':
            print('*** APPLY {} montage'.format(self.inputs.refmethod))
            self.inputs.script = self._bipolar_reference()

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
