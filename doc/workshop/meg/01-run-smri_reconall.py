"""
.. _run_FS:

==================================
01. Freesurfer anatomical pipeline
==================================

The solution of MEG inverse problem requires knowledge of the lead field
matrix. A cortical segmentation of the anatomical MRI is necessary to generate
the source space, where the neural activity will be estimated.
A Boundary Element Model (BEM) which uses the segmented surfaces is used to
construct the lead field matrix. To perform the cortical segmentation we
provide a workflow based on nipype Interface wrapping the
`recon-all <https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all>`_ command of
Freesurfer. The output of recon-all node is used as input of another node that
creates the BEM surfaces using the FreeSurfer watershed algorithm .

.. warning:: Make sure that Freesurfer is properly configured before
    running this script.
"""

###############################################################################
# Import modules
# ^^^^^^^^^^^^^^
import os
import json
import pprint
import os.path as op
import nipype.pipeline.engine as pe

from nipype.interfaces.freesurfer import ReconAll
from nipype.interfaces.utility import Function

from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.compute_fwd_problem import _create_bem_sol

rel_path = op.split(os.path.realpath(__file__))[0]
print('relative path : {}'.format(rel_path))

###############################################################################
# Define data and variables
# ^^^^^^^^^^^^^^^^^^^^^^^^^
# Let us specify the variables that are specific for the data analysis (the
# main directories where the data are stored, the list of subjects and
# sessions, ...) and the variable specific for the particular pipeline
# (MRI path, Freesurfer fir, ...) in a *json* file
# :download:`json <https://github.com/neuropycon/ephypype/tree/master/doc/workshop/meg/params.json>` file 

# Read experiment params as json
params = json.load(open(os.path.join(rel_path, "params.json")))
pprint.pprint({'parameters': params["general"]})

subjects_dir = params["general"]["subjects_dir"]
subject_ids = params["general"]["subject_ids"]
NJOBS = params["general"]["NJOBS"]

if "subjects_dir" in params["general"].keys():
    data_path = params["general"]["subjects_dir"]
else:
    data_path = os.path.expanduser("~")

# Check envoiroment variables
if not os.environ.get('FREESURFER_HOME'):
    raise RuntimeError('FREESURFER_HOME environment variable not set')
os.environ["SUBJECTS_DIR"] = subjects_dir
print('SUBJECTS_DIR %s ' % os.environ["SUBJECTS_DIR"])

# workflow directory within the `base_dir`
freesurfer_workflow_name = 'FS_workflow'
main_workflow = pe.Workflow(name=freesurfer_workflow_name)
main_workflow.base_dir = subjects_dir

# (1) we create a node to pass input filenames to DataGrabber from nipype
#     iterate over subjects
infosource = create_iterator(['subject_id'], [subject_ids])

# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node
# Here we define an input field for datagrabber called subject_id.
# This is then used to set the template (see %s in the template).
# we look for .nii files
template_path = '../%s/ses-mri/anat/%s*T1w.nii.gz'
template_args = [['subject_id', 'subject_id']]
infields = ['subject_id']
datasource = create_datagrabber(data_path, template_path, template_args,
                                infields=infields)

# (2) ReconAll Node to generate surfaces and parcellations of structural
#     data from anatomical images of a subject.
recon_all = pe.Node(interface=ReconAll(), infields=['T1_files'],
                    name='recon_all')
recon_all.inputs.subjects_dir = subjects_dir
recon_all.inputs.directive = 'all'

# reconall_workflow will be a node of the main workflow
reconall_workflow_name = 'segmentation_workflow'
reconall_workflow = pe.Workflow(name=reconall_workflow_name)
reconall_workflow.base_dir = data_path

reconall_workflow.connect(infosource, 'subject_id', datasource,  'subject_id')
reconall_workflow.connect(infosource, 'subject_id', recon_all, 'subject_id')
reconall_workflow.connect(datasource, 'raw_file', recon_all, 'T1_files')

# (3) BEM generation by make_watershed_bem of MNE Python package
bem_generation = pe.Node(interface=Function(
    input_names=['subjects_dir', 'sbj_id'], output_names=['sbj_id'],
    function=_create_bem_sol), name='call_mne_watershed_bem')
bem_generation.inputs.subjects_dir = subjects_dir

main_workflow.connect(reconall_workflow, 'recon_all.subject_id',
                      bem_generation, 'sbj_id')

###############################################################################
# Execute the pipeline
# The code above sets up all the necessary data structures and the connectivity
# between the processes, but does not generate any output. To actually run the
# analysis on the data the ``nipype.pipeline.engine.Pipeline.Run``
# function needs to be called.

main_workflow.write_graph(graph2use='colored')
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})
