"""
===============
02. Compute ERP
===============
This workflow mainly call the ephypype pipeline computing N170 component
from raw data specified by the user. The first Node of the workflow
(extract_events Node) extract the events from raw data. The events are saved
in the Node directory.
In the ERP_pipeline the raw data are epoched accordingly to events extracted in
extract_events Node.
The evoked datasets are created by averaging the different conditions specified
in json file. 
"""
# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

# sphinx_gallery_thumbnail_number = 1


import os.path as op
import json
import pprint  # noqa
import ephypype

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function

from ephypype.nodes import create_iterator, create_datagrabber
from ephypype.pipelines.preproc_meeg import create_pipeline_evoked
from ephypype.datasets import fetch_erpcore_dataset

###############################################################################
# Let us fetch the data first. It is around 90 MB download.
base_path = op.join(op.dirname(ephypype.__file__), '..', 'doc/workshop')
data_path = fetch_erpcore_dataset(base_path)

# Read experiment params as json
params = json.load(open("params.json"))

pprint.pprint({'parameters': params})
print(params["general"])

data_type = params["general"]["data_type"]
subject_ids = params["general"]["subject_ids"]
NJOBS = params["general"]["NJOBS"]
session_ids = params["general"]["session_ids"]

# ERP params
ERP_str = 'ERP'
pprint.pprint({'ERP': params[ERP_str]})
events_id = params[ERP_str]['events_id']
condition = params[ERP_str]['condition']
baseline = tuple(params[ERP_str]['baseline'])
events_file = params[ERP_str]['events_file']
t_min = params[ERP_str]['tmin']
t_max = params[ERP_str]['tmax']


def get_events(raw_ica, subject):
    '''
    The events are extracted from annotation. The events are saved
    to the Node directory.
    We take the ica file from the
    preprocessing workflow directory, i.e. the cleaned raw data.
    '''
    print(subject, raw_ica)
    import mne
    import numpy as np

    rename_events = {
        '201': 'response/correct',
        '202': 'response/error'
    }
    
    for i in range(1, 180+1):
        orig_name = f'{i}'
        
        if 1 <= i <= 40:
            new_name = 'stimulus/face/normal'
        elif 41 <= i <= 80:
            new_name = 'stimulus/car/normal'
        elif 101 <= i <= 140:
            new_name = 'stimulus/face/scrambled'
        elif 141 <= i <= 180:
            new_name = 'stimulus/car/scrambled'
        else:
            continue

        rename_events[orig_name] = new_name

    raw = mne.io.read_raw_fif(raw_ica, preload=True)
    events_from_annot, event_dict  = mne.events_from_annotations(raw)
    
    faces = list()
    car = list()
    for key in event_dict.keys():
    
        if rename_events[key] == 'stimulus/car/normal':
            car.append(event_dict[key])
        elif rename_events[key] == 'stimulus/face/normal':
            faces.append(event_dict[key])
    print(faces)
    print(car)
    merged_events = mne.merge_events(events_from_annot, faces, 1)
    merged_events = mne.merge_events(merged_events, car, 2)
    print(events_from_annot[:10])
    print(merged_events[:10])
    print(np.sum(merged_events[:,2]==1))
    print(np.sum(merged_events[:,2]==2))
        

    event_file = raw_ica.replace('.fif', '-eve.fif')
    mne.write_events(event_file, merged_events)

    return event_file
    

###############################################################################
# Defining pipeline to compute inverse solution
###############################################################################
# Then, we create our workflow and specify the `base_dir` which tells
# nipype the directory in which to store the outputs.


# workflow directory within the `base_dir`
ERP_pipeline_name = ERP_str + '_workflow'

main_workflow = pe.Workflow(name=ERP_pipeline_name)
main_workflow.base_dir = data_path

# We create a node to pass input filenames to DataGrabber from nipype
infosource = create_iterator(['subject_id', 'session_id'],
                             [subject_ids, session_ids])

# and a node to grab data. The template_args in this node iterate upon
# the values in the infosource node
ica_dir = op.join(
        data_path, 'preprocessing_workflow', 'preproc_eeg_pipeline')


template_path = "_session_id_%s_subject_id_%s/ica/sub-%s_ses-%s_*filt_ica.fif"
template_args = [['session_id', 'subject_id', 'subject_id', 'session_id']]
datasource = create_datagrabber(ica_dir, template_path, template_args)


# We connect the output of infosource node to the one of datasource.
# So, these two nodes taken together can grab data.
main_workflow.connect(infosource, 'subject_id', datasource,  'subject_id')
main_workflow.connect(infosource, 'session_id', datasource, 'session_id')

# We define the Node that encapsulates run_events_concatenate function
extract_events = pe.Node(
    Function(input_names=['raw_ica', 'subject'],
             output_names=['event_file'],
             function=get_events),
    name='extract_events')

main_workflow.connect(datasource, 'raw_file',
                      extract_events, 'raw_ica')
main_workflow.connect(infosource, 'subject_id',
                      extract_events, 'subject')

###############################################################################
# Ephypype creates for us a pipeline to compute evoked data which can be
# connected to these nodes we created.
ERP_workflow = create_pipeline_evoked(
        data_path, data_type=data_type, pipeline_name="ERP_pipeline",
        events_id=events_id, baseline=baseline,
        condition=condition, t_min=t_min, t_max=t_max)

main_workflow.connect(infosource, 'subject_id',
                      ERP_workflow, 'inputnode.sbj_id')
main_workflow.connect(datasource, 'raw_file',
                      ERP_workflow, 'inputnode.raw')
main_workflow.connect(extract_events, 'event_file',
                      ERP_workflow, 'inputnode.events_file')

###############################################################################
# To do so, we first write the workflow graph (optional)
main_workflow.write_graph(graph2use='colored')  # colored

# Finally, we are now ready to execute our workflow.
main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}
# Run workflow locally on 1 CPU
main_workflow.run(plugin='LegacyMultiProc', plugin_args={'n_procs': NJOBS})
