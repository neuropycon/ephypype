# -*- coding: utf-8 -*-
"""

Description:

All nodes for import that are NOT specific to a ephy package
"""
import os

from nipype.interfaces.base import BaseInterface,\
    BaseInterfaceInputSpec, traits, TraitedSpec, isdefined

from nipype.interfaces.base import File


# ----------------- ImportMat ----------------------------- #
class ImportMatInputSpec(BaseInterfaceInputSpec):
    """Input specification for ImportMat"""
    tsmat_file = traits.File(exists=True,
                             desc='time series in .mat (matlab format)',
                             mandatory=True)

    data_field_name = traits.String('F', desc='Name of structure in matlab',
                                    usedefault=True)

    good_channels_field_name = traits.String('ChannelFlag',
                                             desc='Boolean structure for\
                                                   choosing nodes, name of\
                                                   structure in matlab file')


class ImportMatOutputSpec(TraitedSpec):
    """Output spec for Import Mat"""

    ts_file = traits.File(exists=True, desc="time series in .npy format")


class ImportMat(BaseInterface):

    """
    Description:

    Import matlab file to numpy ndarry, and save it as numpy file .npy

    Inputs:

    tsmat_file:
        type = File, exists=True, desc='nodes * time series
               in .mat (matlab format format', mandatory=True

    data_field_name
        type = String, default = 'F', desc='Name of the structure in matlab',
        usedefault=True

    good_channels_field_name
        type = String, default = 'ChannelFlag',
               desc='Boolean structure for choosing nodes,
               name of structure in matlab file'

    Outputs:

    ts_file
        type = File, exists=True, desc="time series in .npy format"

    """

    input_spec = ImportMatInputSpec
    output_spec = ImportMatOutputSpec

    def _run_interface(self, runtime):

        from ephypype.import_mat import import_tsmat_to_ts

        tsmat_file = self.inputs.tsmat_file

        data_field_name = self.inputs.data_field_name

        good_channels_field_name = self.inputs.good_channels_field_name

        if not isdefined(good_channels_field_name):
            good_channels_field_name = None

        self.ts_file = import_tsmat_to_ts(
            tsmat_file, data_field_name, good_channels_field_name)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['ts_file'] = self.ts_file

        return outputs


######################################################################################## ImportBrainVisionAscii #####################################################################################################

class ImportBrainVisionAsciiInputSpec(BaseInterfaceInputSpec):

    txt_file = File(exists=True,
                    desc='Ascii text file exported from BrainVision',
                    mandatory=True)

    sample_size = traits.Float(desc='Size (number of time points) of all samples',
                               mandatory=True)

    sep_label_name = traits.String("",
                                   desc='Separator between electrode name \
                                         (normally a capital letter) and contact numbers',
                                   usedefault=True)

    repair = traits.Bool(True,
                         desc='Repair file if behaves strangely (adding space sometimes...)',
                         usedefault=True)

    sep = traits.Str(
        ";", desc="Separator between time points", usedefault=True)

    keep_electrodes = traits.String("",
                                    desc='keep_electrodes',
                                    usedefault=True)


class ImportBrainVisionAsciiOutputSpec(TraitedSpec):
    """Output specification for ImportBrainVisionAscii"""

    splitted_ts_file = traits.File(
        exists=True, desc='splitted time series in .npy format')

    elec_names_file = traits.File(
        exists=True, desc='electrode names in txt format')


class ImportBrainVisionAscii(BaseInterface):

    """
    Description:

    Import IntraEEG Brain Vision (unsplitted) ascii time series txt file and
    return splitted time series in .npy format, as well as electrode names in txt format

    Inputs:

    txt_file
        type = File, exists=True, desc='Ascii text file exported from BrainVision', mandatory=True

    sample_size
        type = Int, desc = "Size (number of time points) of all samples", mandatory = True

    sep_label_name
        type = String, default = "", desc='Separator between electrode name
        (normally a capital letter) and contact numbers', usedefault=True

    repair
        type = Bool, default = True, desc='Repair file if behaves strangely
        (adding space sometimes...)', usedefault  = True

    sep
        type = String, default = ";","Separator between time points",usedefault = True)

    Outputs:

    splitted_ts_file
        type  = File, exists=True, desc="splitted time series in .npy format"

    elec_names_file
        type = File, exists=True, desc="electrode names in txt format"


    """
    input_spec = ImportBrainVisionAsciiInputSpec
    output_spec = ImportBrainVisionAsciiOutputSpec

    def _run_interface(self, runtime):

        from ephypype.import_txt import split_txt

        txt_file = self.inputs.txt_file

        sample_size = self.inputs.sample_size

        sep_label_name = self.inputs.sep_label_name

        repair = self.inputs.repair

        sep = self.inputs.sep

        keep_electrodes = self.inputs.keep_electrodes

        print(keep_electrodes)

        split_txt(txt_file=txt_file, sample_size=sample_size,
                  sep_label_name=sep_label_name, repair=repair, sep=sep, keep_electrodes=keep_electrodes)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['elec_names_file'] = os.path.abspath(
            'correct_channel_names.txt')

        outputs['splitted_ts_file'] = os.path.abspath('splitted_ts.npy')

        return outputs

######################################################################################## ImportBrainVisionVhdr #####################################################################################################


class ImportBrainVisionVhdrInputSpec(BaseInterfaceInputSpec):

    vhdr_file = File(exists=True,
                     desc='Vhdr file exported from BrainVision',
                     mandatory=True)

    sample_size = traits.Float(desc='Size (number of time points) of all samples',
                               mandatory=True)

    keep_electrodes = traits.String("",
                                    desc='keep_electrodes',
                                    usedefault=True)


class ImportBrainVisionVhdrOutputSpec(TraitedSpec):
    """Output specification for ImportBrainVisionVhdr"""

    splitted_ts_file = traits.File(
        exists=True, desc='splitted time series in .npy format')

    elec_names_file = traits.File(
        exists=True, desc='electrode names in txt format')


class ImportBrainVisionVhdr(BaseInterface):

    """
    Description:

    Import IntraEEG Brain Vision (unsplitted) vhdr time series txt file and
    return splitted time series in .npy format, as well as electrode names in txt format

    Inputs:

    vhdr_file
        type = File, exists=True, desc='Ascii text file exported from BrainVision', mandatory=True

    sample_size
        type = Int, desc = "Size (number of time points) of all samples", mandatory = True

    Outputs:

    splitted_ts_file
        type  = File, exists=True, desc="splitted time series in .npy format"

    elec_names_file
        type = File, exists=True, desc="electrode names in txt format"


    """
    input_spec = ImportBrainVisionVhdrInputSpec
    output_spec = ImportBrainVisionVhdrOutputSpec

    def _run_interface(self, runtime):

        from ephypype.import_txt import read_brainvision_vhdr
        import numpy as np

        vhdr_file = self.inputs.vhdr_file

        sample_size = self.inputs.sample_size

        keep_electrodes = self.inputs.keep_electrodes

        np_splitted_ts, ch_names = read_brainvision_vhdr(
            vhdr_file=vhdr_file, sample_size=sample_size)

        np_ch_names = np.array(ch_names, dtype='str')

        if keep_electrodes != "":

            print(keep_electrodes)

            list_keep_electrodes = keep_electrodes.split("-")

            print(list_keep_electrodes)

            keep = np.array(
                [ch_name in list_keep_electrodes for ch_name in ch_names], dtype='int')

            print(keep)
            keep_ch_names = np_ch_names[keep == 1]
            print(keep_ch_names)

            keep_np_splitted_ts = np_splitted_ts[:, keep == 1, :]
            print(keep_np_splitted_ts.shape)

            np_splitted_ts = keep_np_splitted_ts
            np_ch_names = keep_ch_names

        # saving
        ch_names_file = os.path.abspath("correct_channel_names.txt")

        np.savetxt(ch_names_file, np_ch_names, fmt="%s")

        splitted_ts_file = os.path.abspath("splitted_ts.npy")

        np.save(splitted_ts_file, np_splitted_ts)

        # return splitted_ts_file,ch_names_file

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['elec_names_file'] = os.path.abspath(
            'correct_channel_names.txt')

        outputs['splitted_ts_file'] = os.path.abspath('splitted_ts.npy')

        return outputs

######################################################################################## Ep2ts #####################################################################################################


class Ep2tsInputSpec(BaseInterfaceInputSpec):
    """Input specification for Ep2ts"""
    fif_file = File(exists=True, desc='fif file with epochs', mandatory=True)


class Ep2tsOutputSpec(TraitedSpec):
    ''' Output specification for Ep2ts '''
    ts_file = traits.File(exists=True, desc="time series in .npy format")


class Ep2ts(BaseInterface):

    """
    Description:

    Convert electa fif raw or epochs file to numpy matrix format

    Inputs:

    Outputs:

    """

    input_spec = Ep2tsInputSpec
    output_spec = Ep2tsOutputSpec

    def _run_interface(self, runtime):

        from ephypype.fif2ts import ep2ts

        fif_file = self.inputs.fif_file

        self.ts_file = ep2ts(fif_file=fif_file)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['ts_file'] = self.ts_file

        return outputs


class ConvertDs2FifInputSpec(BaseInterfaceInputSpec):
    """Input specification for ImportMat"""
    ds_file = traits.Directory(exists=True,
                               desc='raw .ds file',
                               mandatory=True)


class ConvertDs2FifOutputSpec(TraitedSpec):
    ''' Output spec for Import Mat '''

    fif_file = traits.File(exists=True, desc='raw .fif file')


class ConvertDs2Fif(BaseInterface):

    """
    Description:

    Inputs:

    Outputs:

    """
    input_spec = ConvertDs2FifInputSpec
    output_spec = ConvertDs2FifOutputSpec

    def _run_interface(self, runtime):

        from ephypype.import_ctf import convert_ds_to_raw_fif

        ds_file = self.inputs.ds_file

        self.fif_file = convert_ds_to_raw_fif(ds_file)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs["fif_file"] = self.fif_file

        return outputs
