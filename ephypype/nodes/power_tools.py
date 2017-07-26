# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 15:10:04 2017

@author: pasca
"""

from nipype.interfaces.base import BaseInterface,\
    BaseInterfaceInputSpec, traits, TraitedSpec


class PowerBandInputSpec(BaseInterfaceInputSpec):
    """Input specification for PowerBand"""
    psds_file = traits.File(exists=True,
                            desc='psd tensor and frequencies in .npz format',
                            mandatory=True)

    freq_bands = traits.List(desc='frequency bands', mandatory=True)


class PowerBandOutputSpec(TraitedSpec):
    """Output spec for PowerBand"""

    mean_power_band_file = traits.File(exists=True,
                                       desc="mean psd in bands in .npy format")


class PowerBand(BaseInterface):

    """
    Description:

        Compute mean power spectral density for each frequency band and save it
         as  numpy file .npy

    Inputs:

    psds_file
        type = File, exists=True, desc='psd tensor and frequencies in .npz
               format', mandatory=True

    freq_bands
        type = List of Float, desc='frequency bands', mandatory=True

    Outputs:

    mean_power_band_file
        type = File, exists=True, desc="mean psd in bands in .npy format"

    """

    input_spec = PowerBandInputSpec
    output_spec = PowerBandOutputSpec

    def _run_interface(self, runtime):

        from ephypype.power import compute_mean_band_psd

        psds_file = self.inputs.psds_file
        freq_bands = self.inputs.freq_bands

        self.mean_power_band_file = compute_mean_band_psd(psds_file,
                                                          freq_bands)

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['mean_power_band_file'] = self.mean_power_band_file

        return outputs
