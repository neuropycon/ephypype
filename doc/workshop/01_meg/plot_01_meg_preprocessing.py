"""
.. _preproc_meg:

=======================
02. Preprocess MEG data
=======================
The :ref:`preprocessing pipeline <preproc_meeg>` runs the ICA algorithm for an
automatic removal of eyes and heart related artefacts.
A report is automatically generated and can be used to correct and/or fine-tune
the correction in each subject.
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

# sphinx_gallery_thumbnail_number = 2

###############################################################################
# Import modules
# ^^^^^^^^^^^^^^
# The first step is to import the modules we need in the script. We import
# mainly from |nipype| and |ephypype| packages.
#
# .. |nipype| raw:: html
#
#    <a href="https://nipype.readthedocs.io/en/latest/#" target="_blank">nipype</a>
#
# .. |ephypype| raw:: html
#
#    <a href="https://neuropycon.github.io/ephypype/index.html#ephypype target="_blank">ephypype</a>

import json
import pprint

import os.path as op
import nipype.pipeline.engine as pe

from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.pipelines.preproc_meeg import create_pipeline_preproc_meeg  # noqa


###############################################################################
# Define data and variables
# ^^^^^^^^^^^^^^^^^^^^^^^^^
# Let us specify the variables that are specific for the data analysis (the
# main directories where the data are stored, the list of subjects and
# sessions, ...) and the variables specific for the particular pipeline
# (downsampling frequency, EOG and ECG channels, cut-off frequencies, ...) in a
# |params.json| file
# (if it is does work, try to go on the github page, and right-click "Save As" on the Raw button)
#
#.. |params.json| replace::
#   :download:`json <https://github.com/neuropycon/ephypype/tree/master/doc/workshop/01_meg/params.json>`

# Read experiment params as json
params = json.load(open("params.json"))
pprint.pprint({'parameters': params["general"]})

data_type = params["general"]["data_type"]
subject_ids = params["general"]["subject_ids"]
NJOBS = params["general"]["NJOBS"]
session_ids = params["general"]["session_ids"]

is_short = params["general"]["short"]

if "data_path" in params["general"].keys():
    data_path = params["general"]["data_path"]
else:
    data_path = op.expanduser("~")
print("data_path : %s" % data_path)

###############################################################################
# Then, we read the parameters for preprocessing from the json file and print
# it. In the json file we set : the names of EoG and ECG channels, the
# filter settings, the downsampling frequency, the number of ICA components
# specified as a fraction of explained variance (0.999) and a reject
# dictionary to exclude time segments
pprint.pprint({'preprocessing parameters': params["preprocessing"]})

l_freq = params["preprocessing"]['l_freq']
h_freq = params["preprocessing"]['h_freq']
ECG_ch_name = params["preprocessing"]['ECG_ch_name']
EoG_ch_name = params["preprocessing"]['EoG_ch_name']
variance = params["preprocessing"]['variance']
reject = params["preprocessing"]['reject']
down_sfreq = params["preprocessing"]['down_sfreq']

###############################################################################
# Specify Nodes
# ^^^^^^^^^^^^^
# Before to create a |workflow| we have to create the |nodes| that define the
# workflow itself. In this example the main Nodes are
#
# .. |workflow| raw:: html
#
#     <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_workflow.html" target="_blank">workflow</a>
# 
# .. |nodes| raw:: html
#
#    <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_nodes.html" target="_blank">nodes</a>
#
# * ``infosource`` is a Node that just distributes values
# * ``datasource`` is a |DataGrabber| Node that allows the user to define flexible search patterns which can be parameterized by user defined inputs 
# * ``preproc_meg_pipeline`` is a Node containing the pipeline created by :func:`~ephypype.pipelines.create_pipeline_preproc_meeg`
# 
# .. |DataGrabber| raw:: html
#
#    <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_data_input.html#DataGrabber" target="_blank">DataGrabber</a>

###############################################################################
# .. _meg_infosourcenode:
#
# Infosource
# """"""""""
# The ephypype function :func:`~ephypype.nodes.create_iterator` creates the
# ``infosource`` node that allows to distributes values: when we need to feed
# the different subject names into the workflow we only need a Node that can
# receive the input and distribute those inputs to the workflow.
infosource = create_iterator(['subject_id', 'session_id'],
                             [subject_ids, session_ids])

###############################################################################
# .. _meg_datagrabbernode:
#
# DataGrabber
# """""""""""
# Then we create the ``datasource`` node to grab data. The ephypype function
# :func:`~ephypype.nodes.create_datagrabber`
# creates a node to grab data using |DataGrabber| in Nipype. The DataGrabber
# Interface allows to define flexible search patterns which can be
# parameterized by user defined inputs (such as subject ID, session, etc.).
# In this example we parameterize the pattern search with ``subject_id`` and
# ``session_id``. The ``template_args`` in this node iterates upon the values
# in the ``infosource`` node.
# We look for MEG data contained in ``ses-meg/meg`` folder.

if is_short:
    template_path = '%s/ses-meg/meg_short/*%s*run*%s*sss*.fif'
else:
    template_path = '%s/ses-meg/meg/*%s*run*%s*sss*.fif'
template_args = [['subject_id', 'subject_id', 'session_id']]
datasource = create_datagrabber(data_path, template_path, template_args)

###############################################################################
# .. _preproc_meg_node:
#
# Preprocessing Node
# """"""""""""""""""
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. The preprocessing pipeline is implemented by the function
# :func:`~ephypype.pipelines.preproc_meeg.create_pipeline_preproc_meeg`, thus
# to instantiate this pipeline node, we pass our parameters to it.

preproc_workflow = create_pipeline_preproc_meeg(
    data_path, pipeline_name="preproc_meg_dsamp_pipeline",
    l_freq=l_freq, h_freq=h_freq,
    variance=variance, ECG_ch_name=ECG_ch_name, EoG_ch_name=EoG_ch_name,
    data_type=data_type, down_sfreq=down_sfreq)

###############################################################################
# Specify Workflows and Connect Nodes
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Now, we create our workflow and specify the ``base_dir`` which tells nipype
# the directory in which to store the outputs.

preproc_pipeline_name = 'preprocessing_dsamp_short_workflow'

main_workflow = pe.Workflow(name=preproc_pipeline_name)
main_workflow.base_dir = data_path

###############################################################################
# We then connect the nodes two at a time. First, we connect the two outputs
# (``subject_id`` and ``session_id``) of the :ref:`meg_infosourcenode` node to
# the :ref:`meg_datagrabbernode` node. So, these two nodes taken together can
# grab data

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

###############################################################################
# Similarly, for the inputnode of the :ref:`preproc_meg_node`. Things will
# become clearer in a moment when we plot the graph of the workflow.

main_workflow.connect(infosource, 'subject_id',
                      preproc_workflow, 'inputnode.subject_id')
main_workflow.connect(datasource, 'raw_file',
                      preproc_workflow, 'inputnode.raw_file')

###############################################################################
# Run workflow
# ^^^^^^^^^^^^
# After we have specified all the nodes and connections of the workflow, the
# last step is to run it by calling the ``run`` method. It’s also possible to
# generate static graph representing nodes and connections between them by
# calling ``write_graph`` method.

main_workflow.write_graph(graph2use='colored')  # optional

###############################################################################
# Take a moment to pause and notice how the connections
# here correspond to how we connected the nodes.

import matplotlib.pyplot as plt  # noqa
img = plt.imread(op.join(data_path, preproc_pipeline_name, 'graph.png'))
plt.figure(figsize=(6, 6))
plt.imshow(img)
plt.axis('off')

###############################################################################
# Finally, we are now ready to execute our workflow.
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})

###############################################################################
# Results
# ^^^^^^^
# The output is the preprocessed data stored in the workflow directory
# defined by ``base_dir``. Here we find the folder
# ``preprocessing_dsamp_workflow`` where all the results of each iteration are
# sorted by nodes. The cleaned data will be used in :ref:`plot_events_inverse`.
#
# It’s a good rule to inspect the report file saved in the ``ica`` dir to look
# at the excluded ICA components.
#
# .. note:: You could use this :download:`notebook <https://github.com/neuropycon/ephypype/tree/master/doc/workshop/01_meg/ipynb_preprocessing.ipynb>`
#       to better inspect your ICs

import mne  # noqa
from ephypype.gather import get_results # noqa

ica_files, raw_files = get_results(main_workflow.base_dir,
                                   main_workflow.name, pipeline='ica')

for ica_file, raw_file in zip(ica_files, raw_files):
    print(f'*** {raw_file} ***')
    raw = mne.io.read_raw_fif(raw_file)
    ica = mne.preprocessing.read_ica(ica_file)
    ica.plot_properties(raw, picks=ica.exclude, figsize=[4.5, 4.5])

    # ica.plot_components()
    # ica.plot_sources(raw)
