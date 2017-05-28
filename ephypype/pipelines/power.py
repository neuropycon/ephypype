"""
Power Pipeline
"""
# Authors: Dmitrii Altukhov <dm-altukhov@ya.ru>
#          Annalisa Pascarella <a.pascarella@iac.cnr.it>

import nipype.pipeline.engine as pe

from nipype.interfaces.utility import IdentityInterface
from ephypype.interfaces.mne.power import Power


def create_pipeline_power(main_path, pipeline_name='power',
                          fmin=0, fmax=300, method='welch',
                          is_epoched=False):
    """
    Description:

        Power pipeline: wraps functions of MNE to compute PSD of epoch or raw data

    Inputs:

        main_path : str
            the main path of the pipeline
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

    Inputs (inputnode):

        fif_file : str
            path to raw or epoched meg data in fif format

    Outputs:

        pipeline : instance of Workflow

    """

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    print('*** main_path -> %s' % main_path + ' ***')

    # define the inputs of the pipeline
    inputnode = pe.Node(IdentityInterface(fields=['fif_file']),
                        name='inputnode')

    power_node = pe.Node(interface=Power(), name='power')
    power_node.inputs.fmin = fmin
    power_node.inputs.fmax = fmax
    power_node.inputs.method = method
    power_node.inputs.is_epoched = is_epoched

    pipeline.connect(inputnode, 'fif_file', power_node, 'data_file')

    return pipeline
