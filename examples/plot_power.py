"""
==============
Power pipeline
==============
The power pipeline computes the power spectral density (PSD)
on epochs or raw data on sensor space or source space.
The mean PSD for each selected frequency band is also
computed and saved in a numpy file.
"""

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface
import nipype.interfaces.io as nio

from ephypype.pipelines.power import create_pipeline_power

from params.power import data_path # noqa: E402
from params.power import subject_ids, sessions # noqa: E402
from params.power import power_analysis_name # noqa: E402
from params.power import fmin, fmax, power_method, is_epoched, freq_bands # noqa: E402


def create_infosource():
    """Create node which passes input filenames to DataGrabber"""

    infosource = pe.Node(interface=IdentityInterface(fields=['subject_id',
                                                             'sess_index']),
                         name="infosource")

    infosource.iterables = [('subject_id', subject_ids),
                            ('sess_index', sessions)]

    return infosource


def create_datasource():

    datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id',
                                                             'sess_index'],
                                                   outfields=['raw_file']),
                         name='datasource')

    datasource.inputs.base_directory = data_path
    datasource.inputs.template = '*%s/%s/meg/%s*rest*ica.fif'
    datasource.inputs.template_args = dict(raw_file=[['subject_id',
                                                      'sess_index',
                                                      'subject_id']])
    datasource.inputs.sort_filelist = True

    return datasource


def create_main_workflow_power():

    main_workflow = pe.Workflow(name=power_analysis_name)
    main_workflow.base_dir = data_path

    # info source
    infosource = create_infosource()

    # data source
    datasource = create_datasource()

    main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
    main_workflow.connect(infosource, 'sess_index', datasource, 'sess_index')

    power_workflow = create_pipeline_power(data_path, freq_bands,
                                           fmin=fmin, fmax=fmax,
                                           method=power_method,
                                           is_epoched=is_epoched)

    main_workflow.connect(datasource, 'raw_file',
                          power_workflow, 'inputnode.fif_file')

    return main_workflow


if __name__ == '__main__':

    # run pipeline:
    main_workflow = create_main_workflow_power()

    main_workflow.write_graph(graph2use='colored')  # colored
    main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

    main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 3})
