"""Utilities to import data into M/EEG preprocessing pipelines."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#          Mainak Jas <mainakjas@gmail.com>
#
# License: BSD (3-clause)

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface, Function
import nipype.interfaces.io as nio


def create_iterator(fields, field_values):
    """Create node to iterate on fields.

    Parameters
    ----------
    field : list of str
        The fields to iterate upon., E.g., ['subject_id', 'session_id']
    field_values : list of list
        The values of the field over which to iterate over.
        E.g., [['sub-001', 'sub-002'], ['ses-01']]

    Returns
    -------
    infosource : instance of pe.Node
        The node which iterates on the subject_ids and session_ids.
    """
    if len(fields) != len(field_values):
        raise ValueError('fields and field_values must have'
                         'the same length')

    infosource = pe.Node(interface=IdentityInterface(fields=fields),
                         name="infosource")

    infosource.iterables = [(f, fv) for (f, fv) in zip(fields, field_values)]

    return infosource


def create_datagrabber(data_path, template_path, template_args):
    """Create node to grab data using DataGrabber in Nipype.

    Parameters
    ----------
    data_path : str
        The base directory for the input data.
    template_path : str
        Input filename string (relative to base directory)
        along with string formatters (only %s allowed for now) and
        wildcard characters.
        E.g., '*%s/%s/meg/%s*rest*raw.fif'
    template_args : list of str
        The arguments for the templates. Can be either 'subject_id'
        or 'session_id'

    Returns
    -------
    datasource : instance of pe.Node
        The node which grabs the filenames.
    """

    datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id',
                                                             'session_id'],
                                                   outfields=['raw_file']),
                         name='datasource')

    datasource.inputs.base_directory = data_path
    datasource.inputs.template = template_path

    datasource.inputs.template_args = dict(raw_file=template_args)

    datasource.inputs.sort_filelist = True

    return datasource


def get_frequency_band(freq_band_names, freq_bands):
    """"Create node to get frequency band of interest.

    Parameters
    ----------
    freq_band_names : list of str
        The frequency band names
    freq_bands : list of list
        The interval of frequency bands

    Returns
    -------
    frequency_node : instance of pe.Node
        The node which recover the frequency band of interest.
    """

    from ..aux_tools import _get_freq_band

    frequency_node = pe.Node(interface=Function(
        input_names=['freq_band_name',
                     'freq_band_names',
                     'freq_bands'],
        output_names=['freq_bands'],
        function=_get_freq_band),
        name='get_frequency_node')

    frequency_node.inputs.freq_band_names = freq_band_names
    frequency_node.inputs.freq_bands = freq_bands

    return frequency_node
