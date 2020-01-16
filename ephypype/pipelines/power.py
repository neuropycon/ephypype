"""Power Pipeline.

Authors: Dmitrii Altukhov <dm-altukhov@ya.ru>
         Annalisa Pascarella <a.pascarella@iac.cnr.it>
"""


import nipype.pipeline.engine as pe

from nipype.interfaces.utility import IdentityInterface
from ephypype.interfaces.mne.power import Power
from ephypype.nodes.power_tools import PowerBand


def create_pipeline_power(main_path, freq_bands, pipeline_name='power_pipeline',  # noqa
                          fmin=0, fmax=300, method='welch',
                          is_epoched=False):
    """Power pipeline.

    Wraps functions of MNE to compute PSD of epoch or raw data.

    Parameters
    ----------
    main_path : str
        the main path of the pipeline
    freq_bands : list
        frequency bands
    pipeline_name : str (default 'power')
        name of the pipeline
    fmin : float (default 0)
        min frequency of interest
    fmax : float (default 300)
        max frequency of interest
    method : str (default 'welch')
        if 'welch' the power spectral density (PSD) is computed by Welch's
        method; otherwise, if 'multitaper' the PSD is computed by
        multitapers
    is_epoched : bool (default False)
        True if the input data are in epoch format (-epo.fif); False
        if the input data are raw data (-raw.fif)

    fif_file (inputnode): str
        path to raw or epoched meg data in fif format

    Returns
    -------
    pipeline : instance of Workflow
    """
    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    print(('*** main_path -> %s' % main_path + ' ***'))

    # define the inputs of the pipeline
    inputnode = pe.Node(IdentityInterface(fields=['fif_file']),
                        name='inputnode')

    power_node = pe.Node(interface=Power(), name='power')
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.method = method
    power_node.inputs.is_epoched = is_epoched

    pipeline.connect(inputnode, 'fif_file', power_node, 'data_file')

    power_band_node = pe.Node(interface=PowerBand(), name='power_band')
    power_band_node.inputs.freq_bands = freq_bands

    pipeline.connect(power_node, 'psds_file', power_band_node, 'psds_file')

    return pipeline


def create_pipeline_power_src_space(main_path, sfreq, freq_bands,
                                    pipeline_name='source_power',
                                    fmin=0, fmax=300, nfft=256, overlap=0,
                                    is_epoched=False):
    """Power pipeline: wraps functions of MNE to compute source PSD.

    Parameters
    ----------
    main_path : str
        the main path of the pipeline
    sfreq : float
        sampling frequency
    freq_bands : list
        frequency bands
    pipeline_name : str (default 'source_power')
        name of the pipeline
    fmin : float (default 0)
        min frequency of interest
    fmax : float (default 300)
        max frequency of interest
    n_fft : int (default 256)
        the length of FFT used
    n_overlap : int
        The number of points of overlap between segments
    is_epoched : bool (default False)
        True if the input data are in epoch format

    Inputs (inputnode)
    ------------------
    src_file : str
        path to source reconstruction matrix (.npy format)

    Returns
    -------
    pipeline : instance of Workflow
    """
    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    print('*** main_path -> %s' % main_path + ' ***')

    # define the inputs of the pipeline
    inputnode = pe.Node(IdentityInterface(fields=['data_file']),
                        name='inputnode')

    power_node = pe.Node(interface=Power(), name='power')
    power_node.inputs.sfreq = sfreq
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.nfft = nfft
    power_node.inputs.overlap = overlap
    power_node.inputs.is_epoched = is_epoched
    power_node.inputs.is_sensor_space = False

    pipeline.connect(inputnode, 'data_file', power_node, 'data_file')

    power_band_node = pe.Node(interface=PowerBand(), name='power_band')
    power_band_node.inputs.freq_bands = freq_bands

    pipeline.connect(power_node, 'psds_file', power_band_node, 'psds_file')

    return pipeline
