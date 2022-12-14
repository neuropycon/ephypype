"""
====================================================
04. Preprocess MEG data and compute inverse solution
====================================================
Here we combine the previous pipeline (:ref:`preprocessing pipeline <preproc_meeg>`,
:ref:`plot_events_inverse`) in a unique workflow.
This example shows how to combine the different NeuroPycon pipeline to create
an analysis workflow. 

"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

# sphinx_gallery_thumbnail_number = 1


import json
import pprint  # noqa

import os.path as op
import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface, Function
import nipype.interfaces.io as nio

from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.pipelines.preproc_meeg import create_pipeline_preproc_meeg  # noqa
from ephypype.pipelines.fif_to_inv_sol import create_pipeline_source_reconstruction  # noqa


# Read experiment params as json
params = json.load(open("params.json"))
pprint.pprint({'parameters': params})

data_type = params["general"]["data_type"]
subject_ids = params["general"]["subject_ids"]
NJOBS = params["general"]["NJOBS"]
if "data_path" in params["general"].keys():
    data_path = params["general"]["data_path"]
else:
    data_path = op.expanduser("~")
print("data_path : %s" % data_path)

###############################################################################
# Read the parameters for preprocessing from a json file and print it
pprint.pprint({'preprocessing parameters': params["preprocessing"]})

l_freq = params["preprocessing"]['l_freq']
h_freq = params["preprocessing"]['h_freq']
ECG_ch_name = params["preprocessing"]['ECG_ch_name']
EoG_ch_name = params["preprocessing"]['EoG_ch_name']
variance = params["preprocessing"]['variance']
reject = params["preprocessing"]['reject']
down_sfreq = params["preprocessing"]['down_sfreq']

###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.

# workflow directory within the `base_dir`
wf_name = 'preprocessing_full_inverse'
main_workflow = pe.Workflow(name=wf_name)
main_workflow.base_dir = data_path

###############################################################################
# Then we create a node to pass input filenames to DataGrabber from nipype

infosource = create_iterator(['subject_id'], [subject_ids])

###############################################################################
# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node

template_path = '*'

raw_file = '%s/ses-meg/meg_short/*%s*run*sss*.fif'
trans_file = '%s/ses-meg/meg_short/%s%s.fif'
field_template = dict(raw_file=raw_file, trans_file=trans_file)

template_args = dict(
    raw_file=[['subject_id', 'subject_id']],
    trans_file=[['subject_id', 'subject_id', "-trans"]])

datasource = create_datagrabber(data_path, template_path, template_args,
                                field_template=field_template,
                                infields=['subject_id'],
                                outfields=['raw_file', 'trans_file'])

main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')

###############################################################################
# Ephypype creates for us a pipeline which can be connected to these
# nodes we created. The preprocessing pipeline is implemented by the function
# ephypype.pipelines.preproc_meeg.create_pipeline_preproc_meeg, thus to
# instantiate this pipeline node, we import it and pass our
# parameters to it.

preproc_workflow = create_pipeline_preproc_meeg(
    data_path, l_freq=l_freq, h_freq=h_freq,
    variance=variance, ECG_ch_name=ECG_ch_name, EoG_ch_name=EoG_ch_name,
    data_type=data_type, down_sfreq=down_sfreq, mapnode=True)

main_workflow.connect(infosource, 'subject_id',
                      preproc_workflow, 'inputnode.subject_id')
main_workflow.connect(datasource, 'raw_file',
                      preproc_workflow, 'inputnode.raw_file')

# Source reconstruction
###############################################################################
# Function to extract events from the stimulus channel
###############################################################################


def run_events_concatenate(list_ica_files, subject):
    '''
    The events are extracted from stim channel 'STI101'. The events are saved
    to the Node directory.
    For each subject, the different run are concatenated in one single raw file
    and saved in the Node directory. We take the different run from the
    preprocessing workflow directory, i.e. the cleaned raw data.
    '''

    print(subject, list_ica_files)
    import os
    import mne

    # could be added in a node to come
    mask = 4096 + 256  # mask for excluding high order bits
    delay_item = 0.0345
    min_duration = 0.015

    print("processing subject: %s" % subject)

    raw_list = list()
    events_list = list()
    fname_events_files = []

    print("  Loading raw data")
    for i, run_fname in enumerate(list_ica_files):
        run = i+1

        raw = mne.io.read_raw_fif(run_fname, preload=True)
        events = mne.find_events(raw, stim_channel='STI101',
                                 consecutive='increasing', mask=mask,
                                 mask_type='not_and',
                                 min_duration=min_duration)

        print("  S %s - R %s" % (subject, run))

        fname_events = os.path.abspath('run_%02d-eve.fif' % run)
        mne.write_events(fname_events, events)
        fname_events_files.append(fname_events)

        delay = int(round(delay_item * raw.info['sfreq']))
        events[:, 0] = events[:, 0] + delay
        events_list.append(events)

        raw_list.append(raw)

    raw, events = mne.concatenate_raws(raw_list, events_list=events_list)
    raw.set_eeg_reference(projection=True)
    raw_file = os.path.abspath('{}_sss_filt_dsamp_ica-raw.fif'.format(subject))
    print(raw_file)

    raw.save(raw_file, overwrite=True)

    event_file = os.path.abspath(
            '{}_sss_filt_dsamp_ica-raw-eve.fif'.format(subject))
    mne.write_events(event_file, events)

    del raw_list
    del raw

    return raw_file, event_file, fname_events_files


###############################################################################
# Group average on source level
###############################################################################
def compute_morph_stc(subject, conditions, cond_files, subjects_dir):
    import os.path as op
    import mne

    print("processing subject: %s" % subject)

    # Morph STCs
    stc_morphed_files = []
    for k, cond_file in enumerate(cond_files):
        print(conditions[k])
        print(cond_file)

        stc = mne.read_source_estimate(cond_file)
        print(stc)

        morph = mne.compute_source_morph(
                        stc, subject_from=subject, subject_to='fsaverage',
                        subjects_dir=subjects_dir)
        print(morph)

        stc_morphed = morph.apply(stc)
        print(stc_morphed)

        stc_morphed_file = op.abspath('mne_dSPM_inverse_morph-%s' % (conditions[k]))  # noqa
        stc_morphed.save(stc_morphed_file)

        stc_morphed_files.append(stc_morphed_file)

    return stc_morphed_files


def show_files(files):
    print(files)
    return files


# building full inverse pipeline
def create_full_inv_pipeline(data_path, params,
                             pipeline_name="full_inv_pipeline"):

    # inverse parameters
    pprint.pprint({'inverse parameters': params["inverse"]})

    events_id = params["inverse"]['events_id']
    condition = params["inverse"]['condition']
    t_min = params["inverse"]['tmin']
    t_max = params["inverse"]['tmax']
    spacing = params["inverse"]['spacing']  # oct-6
    snr = params["inverse"]['snr']
    inv_method = params["inverse"]['method']  # dSPM
    parc = params["inverse"]['parcellation']  # aparc

    subjects_dir = op.join(data_path, params["general"]["subjects_dir"])

    # full inverse pipeline
    inv_pipeline = pe.Workflow(name=pipeline_name)
    inv_pipeline.base_dir = data_path

    # define the inputs of the pipeline
    inputnode = pe.Node(
        IdentityInterface(fields=['list_ica_files', 'subject_id', 'trans_file']),  # noqa
        name='inputnode')

    # We connect the output of infosource node to the one of datasource.
    # So, these two nodes taken together can grab data.
    inv_pipeline.connect(infosource, 'subject_id', datasource,  'subject_id')

    # We define the Node that encapsulates run_events_concatenate function
    concat_event = pe.Node(
        Function(input_names=['list_ica_files', 'subject'],
                 output_names=['raw_file', 'event_file', 'fname_events_files'],
                 function=run_events_concatenate),
        name='concat_event')

    # and its connections to the other nodes
    inv_pipeline.connect(inputnode, 'list_ica_files',
                         concat_event, 'list_ica_files')
    inv_pipeline.connect(inputnode, 'subject_id', concat_event, 'subject')

    ###########################################################################
    # Ephypype creates for us a pipeline to compute inverse solution which can
    # be connected to these nodes we created.
    inv_sol_workflow = create_pipeline_source_reconstruction(
        data_path, subjects_dir, spacing=spacing, inv_method=inv_method,
        is_epoched=True, is_evoked=True, events_id=events_id, condition=condition,  # noqa
        t_min=t_min, t_max=t_max, all_src_space=True, parc=parc, snr=snr)

    inv_pipeline.connect(inputnode, 'subject_id',
                         inv_sol_workflow, 'inputnode.sbj_id')
    inv_pipeline.connect(concat_event, ('raw_file', show_files),
                         inv_sol_workflow, 'inputnode.raw')
    inv_pipeline.connect(concat_event, ('event_file', show_files),
                         inv_sol_workflow, 'inputnode.events_file')

    inv_pipeline.connect(inputnode, 'trans_file',
                         inv_sol_workflow, 'inputnode.trans_file')

    conditions = params["inverse"]['new_name_condition']

    # We define the Node that encapsulates compute_morph_stc function
    morph_stc = pe.Node(
        Function(input_names=['subject', 'conditions', 'cond_files', 'subjects_dir'],  # noqa
                output_names=['stc_morphed_files'],
                function=compute_morph_stc),
        name="morph_stc")

    # and its connections to the other nodes
    inv_pipeline.connect(infosource, 'subject_id', morph_stc, 'subject')
    inv_pipeline.connect(inv_sol_workflow, 'inv_solution.stc_files',
                         morph_stc, 'cond_files')

    morph_stc.inputs.conditions = conditions
    morph_stc.inputs.subjects_dir = subjects_dir

    return inv_pipeline


###############################################################################
# Defining pipeline to compute inverse solution
###############################################################################

inv_pipeline = create_full_inv_pipeline(data_path, params)

# and its connections to the other nodes
main_workflow.connect(preproc_workflow, 'ica.ica_file',
                      inv_pipeline, 'inputnode.list_ica_files')
main_workflow.connect(infosource, 'subject_id',
                      inv_pipeline, 'inputnode.subject_id')
main_workflow.connect(datasource, 'trans_file',
                      inv_pipeline, 'inputnode.trans_file')

###############################################################################
# Workflow graph
# """"""""""""""
# To do so, we first write the workflow graph (optional)
main_workflow.write_graph(graph2use='colored')  # colored

# %% 
# Take a moment to pause and notice how the connections
# here correspond to how we connected the nodes.

import matplotlib.pyplot as plt  # noqa
img = plt.imread(op.join(data_path, wf_name, 'graph.png'))
plt.figure(figsize=(7, 7))
plt.imshow(img)
plt.axis('off')

main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})
###############################################################################
# Finally, we are now ready to execute our workflow.
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}

# Run workflow locally on 1 CPU
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})
