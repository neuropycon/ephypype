"""
.. _source_reconstruction:

==========================================
Using ephypype to compute inverse solution
==========================================
The inverse solution pipeline performs source reconstruction starting either
from raw/epoched data (*.fif* format) specified by the user or from the output
of the Preprocessing pipeline (cleaned raw data).
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>

# License: BSD (3-clause)

import os.path as op

import nipype.pipeline.engine as pe

import ephypype
from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.datasets import fetch_omega_dataset


###############################################################################
# Let us fetch the data first. It is around 675 MB download.

data_type = 'fif'
base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_omega_dataset(base_path)
data_path = '/media/pasca/paska/meg_data/omega/sample_BIDS_omega/'

###############################################################################
# then set the parameters for inverse solution

spacing = 'oct-6'    # ico-5 vs oct-6
snr = 1.0            # use smaller SNR for raw data
inv_method = 'MNE'   # sLORETA, MNE, dSPM
parc = 'aparc'       # The parcellation to use: 'aparc' vs 'aparc.a2009s'

# noise covariance matrix filename template
noise_cov_fname = '*noise*.ds'

# set sbj dir path, i.e. where the FS folfers are
sbj_dir = '/home/pasca/Science/research/MEG/work/subjects'

###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

# workflow directory within the `base_dir`
src_reconstruction_pipeline_name = 'source_reconstruction' + \
                                    inv_method + '_' + parc.replace('.', '')

main_workflow = pe.Workflow(name=src_reconstruction_pipeline_name)
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
template_path = '*%s/%s/meg/%s*rest*short*ica.fif'
template_args = [['subject_id', 'session_id', 'subject_id']]
datasource = create_datagrabber(data_path, template_path, template_args)

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. The inverse solution pipeline is implemented by the
# function :func:`ephypype.pipelines.preproc_meeg.create_pipeline_source_reconstruction`,  # noqa
# thus to instantiate the inverse pipeline node, we import it and pass our
# parameters to it.
# The inverse pipeline contains three nodes that wrap the MNE Python functions
# that perform the source reconstruction steps.
#
# In particular, the three nodes are:
#
# * :class:`ephypype.interfaces.mne.LF_computation.LFComputation` compute the
#   Lead Field matrix
# * :class:`ephypype.interfaces.mne.Inverse_solution.NoiseCovariance` computes
#   the noise covariance matrix
# * :class:`ephypype.interfaces.mne.Inverse_solution.InverseSolution` estimates
#   the time series of the neural sources on a set of dipoles grid

from ephypype.pipelines.fif_to_inv_sol import create_pipeline_source_reconstruction  # noqa
inv_sol_workflow = create_pipeline_source_reconstruction(
        data_path, sbj_dir, spacing=spacing, inv_method=inv_method, parc=parc,
        noise_cov_fname=noise_cov_fname)

###############################################################################
# We then connect the nodes two at a time. First, we connect the two outputs
# (subject_id and session_id) of the infosource node to the datasource node.
# So, these two nodes taken together can grab data.

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

###############################################################################
# Similarly, for the inputnode of the preproc_workflow. Things will become
# clearer in a moment when we plot the graph of the workflow.

main_workflow.connect(infosource, 'subject_id',
                      inv_sol_workflow, 'inputnode.sbj_id')
main_workflow.connect(datasource, 'raw_file',
                      inv_sol_workflow, 'inputnode.raw')

###############################################################################
# To do so, we first write the workflow graph (optional)

main_workflow.write_graph(graph2use='colored')  # colored

###############################################################################
# and visualize it. Take a moment to pause and notice how the connections
# here correspond to how we connected the nodes.

from scipy.misc import imread # noqa
import matplotlib.pyplot as plt # noqa
img = plt.imread(op.join(data_path, src_reconstruction_pipeline_name, 'graph.png'))
plt.figure(figsize=(8, 8))
plt.imshow(img)
plt.axis('off')

###############################################################################
# Finally, we are now ready to execute our workflow.

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 3 CPUs
main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 3})

###############################################################################
# The output is the source reconstruction matrix stored in the workflow
# directory defined by `base_dir`. This matrix can be used as input of
# the Connectivity pipeline.
#
# .. warning:: Before to use this pipeline, we need for each subject a template
#   MRI or the individual MRI data.
