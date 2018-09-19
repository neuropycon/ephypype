"""
======================================
Using ephypype to preprocess your data
======================================
The preprocessing pipeline runs the ICA algorithm for an
automatic removal of eyes and heart related artefacts.
A report is automatically generated and can be used to correct
and/or fine-tune the correction in each subject
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#          Mainak Jas <mainakjas@gmail.com>

# License: BSD (3-clause)

import os.path as op

import nipype.pipeline.engine as pe
import nipype.interfaces.io as nio

from nipype.interfaces.utility import IdentityInterface

import ephypype
from ephypype.datasets import fetch_omega_dataset

###############################################################################
# Let us fetch the data first. It is around 675 MB download.

data_type = 'ds'
base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_omega_dataset(base_path)

###############################################################################
# and define the subject_id and sessions

subject_ids = ['sub-0003']  # 'sub-0004', 'sub-0006'
sessions = ['ses-0001']

down_sfreq = 800
l_freq = 0.1
h_freq = 150

###############################################################################
# then set the ICA variables

is_ICA = True  # if True we apply ICA to remove ECG and EoG artifacts

###############################################################################
# specify ECG and EoG channel names if we know them

ECG_ch_name = 'ECG'
EoG_ch_name = 'HEOG, VEOG'
variance = 0.95

###############################################################################
# and a few more parameters

reject = dict(mag=5e-12, grad=5000e-13)

# pipeline directory within the main_path dir
preproc_pipeline_name = 'preprocessing_pipeline'

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype


def create_infosource():
    """Create node which passes input filenames to DataGrabber"""

    infosource = pe.Node(interface=IdentityInterface(fields=['subject_id',
                                                             'sess_index']),
                         name="infosource")

    infosource.iterables = [('subject_id', subject_ids),
                            ('sess_index', sessions)]

    return infosource


###############################################################################
# and a node to grab data.

def create_datasource():
    """"Create node to grab data"""

    datasource = pe.Node(interface=nio.DataGrabber(infields=['subject_id',
                                                             'sess_index'],
                                                   outfields=['raw_file']),
                         name='datasource')

    datasource.inputs.base_directory = data_path
    datasource.inputs.template = '*%s/%s/meg/%s*rest*.ds'

    datasource.inputs.template_args = dict(raw_file=[['subject_id',
                                                      'sess_index',
                                                      'subject_id']])

    datasource.inputs.sort_filelist = True

    return datasource


###############################################################################
# Finally, we create our workflow

main_workflow = pe.Workflow(name=preproc_pipeline_name)
main_workflow.base_dir = data_path

###############################################################################
# and create the nodes to grab the data

infosource = create_infosource()
datasource = create_datasource()

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. To instantiate the preprocessing node, we import it
# and pass our parameters to it.

from ephypype.pipelines.preproc_meeg import create_pipeline_preproc_meeg # noqa
preproc_workflow = create_pipeline_preproc_meeg(
    data_path, l_freq=l_freq, h_freq=h_freq, down_sfreq=down_sfreq,
    variance=variance, ECG_ch_name=ECG_ch_name, EoG_ch_name=EoG_ch_name,
    data_type=data_type)

###############################################################################
# We then connect the nodes two at a time

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
main_workflow.connect(infosource, 'sess_index', datasource, 'sess_index')
main_workflow.connect(infosource, 'subject_id',
                      preproc_workflow, 'inputnode.subject_id')
main_workflow.connect(datasource, 'raw_file',
                      preproc_workflow, 'inputnode.raw_file')

###############################################################################
# Now, write the workflow graph (optional)

main_workflow.write_graph(graph2use='colored')  # colored

###############################################################################
# and visualize it

from scipy.misc import imread # noqa
import matplotlib.pyplot as plt # noqa
img = plt.imread(op.join(data_path, 'preprocessing_pipeline', 'graph.png'))
plt.figure(figsize=(8, 8))
plt.imshow(img)
plt.axis('off')

###############################################################################
# And finally execute the workflow

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 3 CPUs
main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 3})

###############################################################################
# Now leave a comment about the outputs and where they are stored.
