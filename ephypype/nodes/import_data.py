# -*- coding: utf-8 -*-
"""All nodes for import data in different formats (mat, hdf5, fif, ds,
brainvision)."""

import os
import numpy as np

from nipype.interfaces.base import BaseInterface,\
    BaseInterfaceInputSpec, traits, TraitedSpec, isdefined
from nipype.interfaces.base import File

from ..import_data import _import_tsmat_to_ts, _read_hdf5
from ..import_data import _split_txt, _read_brainvision_vhdr
from ..import_data import _convert_ds_to_raw_fif, _read_fieldtrip_epochs
from ..fif2array import _ep2ts, _get_raw_array


# ----------------- ImportMat ----------------------------- #
class ImportMatInputSpec(BaseInterfaceInputSpec):
    """Input specification for ImportMat."""

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
    """Output spec for Import Mat."""

    ts_file = traits.File(exists=True, desc="time series in .npy format")


class ImportMat(BaseInterface):
    """Import matlab file to numpy ndarry, and save it as numpy file .npy.

    Inputs
    ------
    tsmat_file : str
        Name of the .mat file containing time series matrix whose dimension is
        n_nodes x n_time_points where nodes could be channels, voxels or ROIs
    data_field_name : str
        Name of the structure in matlab containing the data
    good_channels_field_name : str
        Name of structure in matlab containing the channels

    Outputs
    -------
    ts_file : str
        Name of the .npy file where the time series matrix is saved
    """

    input_spec = ImportMatInputSpec
    output_spec = ImportMatOutputSpec

    def _run_interface(self, runtime):

        tsmat_file = self.inputs.tsmat_file
        data_field_name = self.inputs.data_field_name
        good_channels_field_name = self.inputs.good_channels_field_name

        if not isdefined(good_channels_field_name):
            good_channels_field_name = None

        self.ts_file = _import_tsmat_to_ts(
            tsmat_file, data_field_name, good_channels_field_name)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['ts_file'] = self.ts_file

        return outputs


# ----------------- ImportHdf5 ----------------------------- #
class ImportHdf5InputSpec(BaseInterfaceInputSpec):
    """Input specification for ImportHdf5"""

    ts_hdf5_file = traits.File(exists=True,
                               desc='time series in .hdf5 (hdf5 format)',
                               mandatory=True)
    data_field_name = traits.String('dataset', desc='Name of dataset',
                                    usedefault=True)

    transpose = traits.Bool(
        False, usedefault=True,
        desc="If the matlab data have to be transposed once read")


class ImportHdf5OutputSpec(TraitedSpec):
    """Output spec for ImportHdf5"""

    ts_data = traits.Array(exists=True, desc="time series in array format")


class ImportHdf5(BaseInterface):

    """
    Description:

    Import hdf5 file to numpy ndarry

    Inputs
    ------
    ts_hdf5_file : str
        Name of the .hdf5 file containing time series matrix whose dimension is
        n_nodes x n_time_points where nodes could be channels, voxels or ROIs

    data_field_name : string
        Name of the dataset

    transpose:
        type = Bool
        default = False, usedefault = True,
        desc = "If the matlab data have to be transposed once read")

    Outputs
    -------
    ts_data : str
        Name of the .npy file where the time series matrix is saved
    """

    input_spec = ImportHdf5InputSpec
    output_spec = ImportHdf5OutputSpec

    def _run_interface(self, runtime):

        ts_hdf5_file = self.inputs.ts_hdf5_file
        data_field_name = self.inputs.data_field_name

        self.ts_data = _read_hdf5(ts_hdf5_file, dataset_name=data_field_name,
                                  transpose=self.inputs.transpose)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['ts_data'] = self.ts_data

        return outputs


# ------------------- ImportBrainVisionAscii ------------------- #
class ImportBrainVisionAsciiInputSpec(BaseInterfaceInputSpec):
    """Import brainvision ascii input spec."""

    txt_file = File(exists=True,
                    desc='Ascii text file exported from BrainVision',
                    mandatory=True)
    sample_size = traits.Float(desc='Size (nb of time points) of all samples',
                               mandatory=True)
    sep_label_name = traits.String("",
                                   desc='Separator between electrode name \
                                         (normally a capital letter) and \
                                         contact numbers',
                                   usedefault=True)
    repair = traits.Bool(True,
                         desc='Repair file if behaves strangely (adding \
                         space sometimes...)',
                         usedefault=True)
    sep = traits.Str(
        ";", desc="Separator between time points", usedefault=True)
    keep_electrodes = traits.String("",
                                    desc='keep_electrodes',
                                    usedefault=True)


class ImportBrainVisionAsciiOutputSpec(TraitedSpec):
    """Output specification for ImportBrainVisionAscii."""

    splitted_ts_file = traits.File(
        exists=True, desc='splitted time series in .npy format')
    elec_names_file = traits.File(
        exists=True, desc='electrode names in txt format')


class ImportBrainVisionAscii(BaseInterface):
    """Import IntraEEG Brain Vision (unsplitted) ascii time series txt file.

    The splitted time series in .npy format, as well as electrode names in txt
    format

    Inputs
    ------
    txt_file : str
        Name of the ascii text file exported from BrainVision
    sample_size : int
        Size (number of time points) of all samples
    sep_label_name : str
        Separator between electrode name (normally a capital letter) and
        contact numbers
    repair : bool
        If True repair file if behaves strangely (adding space sometimes...)
    sep : str
        Separator between time points. By default is ';'

    Outputs
    -------
    splitted_ts_file
        Name of the .npy file with the splitted time series
    elec_names_file : str
        Name of the .txt file with electrode names
    """

    input_spec = ImportBrainVisionAsciiInputSpec
    output_spec = ImportBrainVisionAsciiOutputSpec

    def _run_interface(self, runtime):

        txt_file = self.inputs.txt_file
        sample_size = self.inputs.sample_size
        sep_label_name = self.inputs.sep_label_name
        repair = self.inputs.repair
        sep = self.inputs.sep
        keep_electrodes = self.inputs.keep_electrodes

        print(keep_electrodes)

        _split_txt(txt_file=txt_file, sample_size=sample_size,
                   sep_label_name=sep_label_name, repair=repair, sep=sep,
                   keep_electrodes=keep_electrodes)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['elec_names_file'] = os.path.abspath(
            'correct_channel_names.txt')
        outputs['splitted_ts_file'] = os.path.abspath('splitted_ts.npy')

        return outputs


# ------------------- ImportBrainVisionVhdr ------------------- #
class ImportBrainVisionVhdrInputSpec(BaseInterfaceInputSpec):
    """Import brainvision vhdr inut spec."""

    vhdr_file = File(exists=True,
                     desc='Vhdr file exported from BrainVision',
                     mandatory=True)
    sample_size = traits.Float(desc='Size (number of time points) of all \
                               samples', mandatory=True)
    keep_electrodes = traits.String("",
                                    desc='keep_electrodes',
                                    usedefault=True)


class ImportBrainVisionVhdrOutputSpec(TraitedSpec):
    """Output specification for ImportBrainVisionVhdr."""

    splitted_ts_file = traits.File(
        exists=True, desc='splitted time series in .npy format')
    elec_names_file = traits.File(
        exists=True, desc='electrode names in txt format')


class ImportBrainVisionVhdr(BaseInterface):
    """Import IntraEEG Brain Vision (unsplitted) vhdr time series txt file.

    Then splitted time series in .npy format, as well as electrode names in txt
    format

    Inputs
    ------
    vhdr_file : str
        Name of the ascii text file exported from BrainVision
    sample_size : int
        Size (number of time points) of all samples

    Outputs
    -------
    splitted_ts_file : str
        Name of the .npy file with the splitted time series
    elec_names_file : str
        Name of the .txt file with electrode names
    """

    input_spec = ImportBrainVisionVhdrInputSpec
    output_spec = ImportBrainVisionVhdrOutputSpec

    def _run_interface(self, runtime):

        vhdr_file = self.inputs.vhdr_file
        sample_size = self.inputs.sample_size
        keep_electrodes = self.inputs.keep_electrodes

        np_splitted_ts, ch_names = _read_brainvision_vhdr(
            vhdr_file=vhdr_file, sample_size=sample_size)
        np_ch_names = np.array(ch_names, dtype='str')

        if keep_electrodes != "":

            print(keep_electrodes)
            list_keep_electrodes = keep_electrodes.split("-")
            print(list_keep_electrodes)

            lst = [ch_name in list_keep_electrodes for ch_name in ch_names]
            keep = np.array(lst, dtype='int')

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

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['elec_names_file'] = os.path.abspath(
            'correct_channel_names.txt')
        outputs['splitted_ts_file'] = os.path.abspath('splitted_ts.npy')

        return outputs


# ------------------- Ep2ts ------------------- #
class Ep2tsInputSpec(BaseInterfaceInputSpec):
    """Input specification for Ep2ts."""

    fif_file = File(exists=True, desc='fif file with epochs', mandatory=True)


class Ep2tsOutputSpec(TraitedSpec):
    """Output specification for Ep2ts."""

    ts_file = traits.File(exists=True, desc="time series in .npy format")


class Ep2ts(BaseInterface):
    """Convert electa epoched data file to numpy matrix format.

    Inputs
    ------
    fif_file : str
        Name of the fif file with epoched data

    Outputs
    -------
    ts_file : str
        Name of the .npy file with time series
    """

    input_spec = Ep2tsInputSpec
    output_spec = Ep2tsOutputSpec

    def _run_interface(self, runtime):

        fif_file = self.inputs.fif_file
        self.ts_file = _ep2ts(fif_file=fif_file)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['ts_file'] = self.ts_file

        return outputs


# ------------------- ds2fif --------------------------- #
class ConvertDs2FifInputSpec(BaseInterfaceInputSpec):
    """Input specification for ConvertDs2Fif."""

    ds_file = traits.Directory(exists=True,
                               desc='raw .ds file',
                               mandatory=True)


class ConvertDs2FifOutputSpec(TraitedSpec):
    """Output spec for Import Mat."""

    fif_file = traits.File(exists=True, desc='raw .fif file')


class ConvertDs2Fif(BaseInterface):
    """.ds to fif conversion.

    Inputs
    ------
    ds_file : str
        Name of the raw data in ds format

    Outputs
    -------
    fif_file : str
        Name of the raw data converted from ds to fif format
    """

    input_spec = ConvertDs2FifInputSpec
    output_spec = ConvertDs2FifOutputSpec

    def _run_interface(self, runtime):

        ds_file = self.inputs.ds_file
        self.fif_file = _convert_ds_to_raw_fif(ds_file)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs["fif_file"] = self.fif_file

        return outputs


# ------------------- fif2npy --------------------------- #
class Fif2ArrayInputSpec(BaseInterfaceInputSpec):
    """Input specification for Fif2Array."""

    fif_file = File(exists=True, desc='fif file', mandatory=True)


class Fif2ArrayOutputSpec(TraitedSpec):
    """Output specification for Fif2Array."""

    array_file = traits.File(exists=True, desc="time series in .npy format")
    channel_coords_file = traits.File(
        exists=True, desc="channels coordinates in .txt format")
    channel_names_file = traits.File(
        exists=True, desc="channels labels in .txt format")
    sfreq = traits.Float(desc='sampling frequency', mandatory=True)


class Fif2Array(BaseInterface):
    """Import Elekta raw data in .fif format.

    Save the data time series in .npy format, as well as the channels names
    and location in txt format.

    Inputs
    ------
    fif_file : str
        Name of the file file

    Outputs
    -------
    array_file : str
        Name of the .npy file with data time series
    channel_coords_file : str
        Name of the .txt file with channels coordinates
    channel_names_file : str
        Name of the .txt file with channels names
    sfreq : float
        Sampling frequency
    """

    input_spec = Fif2ArrayInputSpec
    output_spec = Fif2ArrayOutputSpec

    def _run_interface(self, runtime):

        fif_file = self.inputs.fif_file

        self.array_file, self.channel_coords_file, self.channel_names_file, \
            self.sfreq = _get_raw_array(fif_file)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs['array_file'] = self.array_file
        outputs['channel_coords_file'] = self.channel_coords_file
        outputs['channel_names_file'] = self.channel_names_file
        outputs['sfreq'] = self.sfreq

        return outputs


# ------------------- FT2fif --------------------------- #
class ImportFieldTripEpochsInputSpec(BaseInterfaceInputSpec):
    """Input specification for ImportFieldTripEpochs."""

    epo_mat_file = traits.File(exists=True,
                               desc='filename of the .mat file containing the data.',  # noqa
                               mandatory=True)
    data_field_name = traits.String('data', desc='Name of structure in matlab',
                                    usedefault=True)


class ImportFieldTripEpochsOutputSpec(TraitedSpec):
    """Output spec for ImportFieldTripEpochs"""

    fif_file = traits.File(exists=True, desc='.fif file containing the data')


class ImportFieldTripEpochs(BaseInterface):
    """Load epoched data from a FieldTrip structure.

    Inputs
    ------
    epo_mat_file : str
        path of the .mat file containing the FieldTrip data

    data_field_name : str
        Name of the structure in matlab containing the data

    Outputs
    -------
    fif_file : str
        Name of the file in fif format containing the loaded data
    """

    input_spec = ImportFieldTripEpochsInputSpec
    output_spec = ImportFieldTripEpochsOutputSpec

    def _run_interface(self, runtime):

        epo_mat_file = self.inputs.epo_mat_file
        data_field_name = self.inputs.data_field_name

        self.fif_file = _read_fieldtrip_epochs(epo_mat_file, data_field_name)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs["fif_file"] = self.fif_file

        return outputs
