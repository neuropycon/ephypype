"""
.. _ft_example:

======================================
Compute average regerence on ECoG data
======================================
This pipeline shows a very simple example on how to create a pipeline wrapping
a desired function of a Matlab toolbox (FieldTrip).

The **input** data should be a **.mat** file containing a data struct accepeted
by FieldTrip
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

import os.path as op
import nipype.pipeline.engine as pe

import ephypype
from ephypype.nodes import create_iterator, create_datagrabber
from FT_tools import Reference
from ephypype.datasets import fetch_ieeg_dataset


###############################################################################
# Let us fetch the data first. It is around 675 MB download.

data_type = 'fif'
base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_ieeg_dataset(base_path)

ft_path = '/usr/local/MATLAB/R2018a/toolbox/MEEG/fieldtrip-20200327/'
updatesens = 'no'
refmethod = 'avg'
channels_name = '{\'LPG*\', \'LTG*\'}'

workflow_name = 'workflow'

main_workflow = pe.Workflow(name=workflow_name)
main_workflow.base_dir = data_path

subject_ids = ['SubjectUCI29']
infosource = create_iterator(['subject_id'], [subject_ids])

template_path = '%s*.mat'
template_args = [['subject_id']]
datasource = create_datagrabber(data_path, template_path, template_args,
                                infields=['subject_id'])

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')

reference_node = pe.Node(interface=Reference(), name='Reference')
reference_node.inputs.channels = channels_name
reference_node.inputs.ft_path = ft_path
reference_node.inputs.updatesens = updatesens
reference_node.inputs.refmethod = refmethod
reference_node.inputs.script = ''

main_workflow.connect(datasource, 'raw_file', reference_node, 'data_file')
print('*****'.format(reference_node.outputs))

main_workflow.write_graph(graph2use='colored')  # colored
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 1})
