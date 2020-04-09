"""
.. _ft_wf_seeg_example:

====================================
Time-frequency analysis on sEEG data
====================================
This pipeline shows a very simple example on how to create a workflow
connecting a Node that wraps a desired function of a Matlab toolbox
(|FieldTrip|) with a Node that wraps a function of a python toolbox (|MNE|)

.. |FieldTrip| raw:: html

    <a href="http://www.fieldtriptoolbox.org/" target="_blank">FieldTrip</a>

.. |MNE| raw:: html

    <a href="https://mne.tools/stable/index.html" target="_blank">MNE</a>

The **input** data should be a **.mat** file containing a FieldTrip data
structure.
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

# sphinx_gallery_thumbnail_number = 2

import os.path as op
import numpy as np
import nipype.pipeline.engine as pe

import ephypype
from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.nodes import ImportFieldTripEpochs, Reference
from ephypype.interfaces import TFRmorlet
from ephypype.datasets import fetch_ieeg_dataset


###############################################################################
# Let us fetch the data first. It is around 200 MB download. We use the
# intracranial EEG (iEEG) data of SubjectUCI29 data available |here|
#
# .. |here| raw:: html
#
#    <a href="https://zenodo.org/record/1201560#.XoXw8c1S9j4" target="_blank">here</a>

base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_ieeg_dataset(base_path)

###############################################################################
# then read the parameters for time frequency analysis from a
# :download:`json <https://github.com/neuropycon/ephypype/blob/master/examples/params.json>`
# file and print it
#
# .. note:: The code needs the FieldTrip package installed, with path properly setup, for this example to run.

import json  # noqa
import pprint  # noqa
params = json.load(open("params.json"))
pprint.pprint({'time frequency parameters': params["tfr"]})
ft_path = params["tfr"]['fieldtrip_path']
refmethod = params["tfr"]['refmethod']
channels_name = params["tfr"]['channels_name']

###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

workflow_name = 'time_frequency_analysis'

main_workflow = pe.Workflow(name=workflow_name)
main_workflow.base_dir = data_path

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype

subject_ids = ['SubjectUCI29']
infosource = create_iterator(['subject_id'], [subject_ids])

###############################################################################
# and a node to grab data.

template_path = '%s*.mat'
template_args = [['subject_id']]
datasource = create_datagrabber(data_path, template_path, template_args,
                                infields=['subject_id'])

###############################################################################
# We then the output (subject_id) of the infosource node to the datasource one.
# So, these two nodes taken together can grab data.
main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')

###############################################################################
# Now, the :class:`ephypype.nodes.Reference` interface is encapsulated in a
# node and connected to the datasource node.
# We set the channel names of sEEG data and refmethod equal to 'bipolar' in
# order to apply a bipolar montage to the depth electrodes.

reference_node = pe.Node(interface=Reference(), name='rereference')
reference_node.inputs.channels = channels_name
reference_node.inputs.ft_path = ft_path
reference_node.inputs.refmethod = refmethod
reference_node.inputs.script = ''

# Then we connect the output of datasource node to the input of reference_node
main_workflow.connect(datasource, 'raw_file', reference_node, 'data_file')

###############################################################################
# The output of the reference_node will be a FieldTrip data structure
# containing the sEEG data in bipolar montage. Now we create and connect
# two new nodes (import_epochs, compute_tfr_morlet) that convert the FieldTrip
# data in MNE format and compute time-frequency representation of the
# data using |Morlet_wavelets| rispectively.
#
# .. |Morlet_wavelets| raw:: html
#
#    <a href="https://mne.tools/stable/generated/mne.time_frequency.tfr_morlet.html#mne.time_frequency.tfr_morlet" target="_blank">Morlet wavelets</a>

import_epochs = pe.Node(interface=ImportFieldTripEpochs(), name='import_epochs')  # noqa
import_epochs.inputs.data_field_name = 'reref_data'

main_workflow.connect(reference_node, 'data_output',
                      import_epochs, 'epo_mat_file')

compute_tfr_morlet = pe.Node(interface=TFRmorlet(), name='tfr_morlet')
compute_tfr_morlet.inputs.freqs = np.arange(1, 150, 2)

main_workflow.connect(import_epochs, 'fif_file',
                      compute_tfr_morlet, 'epo_file')

###############################################################################
# Finally, we are now ready to execute our workflow. Before, we plot the
# graph of the workflow (optional)

main_workflow.write_graph(graph2use='colored')  # colored

###############################################################################
# and visualize it. Take a moment to pause and notice how the connections
# here correspond to how we connected the nodes.

import matplotlib.pyplot as plt  # noqa
img = plt.imread(op.join(data_path, workflow_name, 'graph.png'))
plt.figure(figsize=(6, 6))
plt.imshow(img)
plt.axis('off')
main_workflow.write_graph(graph2use='colored')  # colored
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 1})

###############################################################################
# To visualize the results we first grab it from workflow directort (base_dir)
# and use an MNE |visualization_function|
#
# .. |visualization_function| raw:: html
#
#    <a href="https://mne.tools/stable/generated/mne.time_frequency.AverageTFR.html#mne.time_frequency.AverageTFR.plot" target="_blank">visualization function </a>

import mne  # noqa
from ephypype.gather import get_results  # noqa

tfr_files, _ = get_results(main_workflow.base_dir,
                           main_workflow.name, pipeline='tfr_morlet')

for tfr_file in tfr_files:
    power = mne.time_frequency.read_tfrs(tfr_file)
    power[0].plot([0], baseline=(-.3, -.1), mode='logratio',
                  title=power[0].ch_names[1])
