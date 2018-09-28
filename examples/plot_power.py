"""
=============================================
Using ephypype to compute PSD on sensor space
=============================================
The power pipeline computes the power spectral density (PSD)
on epochs or raw data on sensor space or source space.
The mean PSD for each selected frequency band is also
computed and saved in a numpy file.
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#          Mainak Jas <mainakjas@gmail.com>

# License: BSD (3-clause)

import os.path as op

import nipype.pipeline.engine as pe

import ephypype
from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.datasets import fetch_omega_dataset


###############################################################################
# Let us fetch the data first. It is around 675 MB download.

base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_omega_dataset(base_path)

###############################################################################
# then set the parameters for PSD computation

# filtering
freq_bands = [[2, 4], [5, 7], [8, 12], [13, 29], [30, 59], [60, 90]]
freq_band_names = ['delta', 'theta', 'alpha', 'beta', 'gamma1', 'gamma2']

is_epoched = False

fmin = 0.1
fmax = 150
sfreq = 600
power_method = 'welch'  # for sensor PSD
n_fft = 2048  # the FFT size (n_fft). Ideally a power of 2

overlap = 0.5  # if is_epoched = False

###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

main_workflow = pe.Workflow(name='power_pipeline')
main_workflow.base_dir = data_path

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype

subject_ids = ['sub-0003']  # 'sub-0004', 'sub-0006'
session_ids = ['ses-0001']
infosource = create_iterator(['subject_id', 'session_id'],
                             [subject_ids, session_ids])

###############################################################################
# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node

template_path = '*%s/%s/meg/%s*rest*ica.fif'
template_args = [['subject_id', 'session_id', 'subject_id']]
datasource = create_datagrabber(data_path, template_path, template_args)

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. To instantiate the power node, we import it
# and pass our parameters to it.

from ephypype.pipelines.power import create_pipeline_power # noqa
power_workflow = create_pipeline_power(data_path, freq_bands,
                                       fmin=fmin, fmax=fmax,
                                       method=power_method,
                                       is_epoched=is_epoched)

###############################################################################
# We then connect the nodes two at a time. First, we connect the two outputs
# (subject_id and session_id) of the infosource node to the datasource node.
# So, these two nodes taken together can grab data.

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

###############################################################################
# Similarly, for the inputnode of the power_workflow. Things will become
# clearer in a moment when we plot the graph of the workflow.

main_workflow.connect(datasource, 'raw_file',
                      power_workflow, 'inputnode.fif_file')


###############################################################################
# To do so, we first write the workflow graph (optional)

main_workflow.write_graph(graph2use='colored')  # colored

###############################################################################
# and visualize it. Take a moment to pause and notice how the connections
# here correspond to how we connected the nodes.

from scipy.misc import imread # noqa
import matplotlib.pyplot as plt # noqa
img = plt.imread(op.join(data_path, 'power_pipeline', 'graph.png'))
plt.figure(figsize=(8, 8))
plt.imshow(img)
plt.axis('off')

###############################################################################
# Finally, we are now ready to execute our workflow.

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 3 CPUs
main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 1})
