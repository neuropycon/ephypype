.. _howto:

   
How to build a Workflow
=======================

The following section is a brief introduction on how to build a Workflow by using NeuroPycon package.

This example script allows to construct a pipeline to compute Power Spectral Density (PSD) in sensor space
(see :ref:`power` Example). 

.. note:: This section is based on the |nipype_beginner|

.. |nipype_beginner| raw:: html

   <a href="https://miykael.github.io/nipype_tutorial/" target="_blank">Nipype Tutorial</a>


.. contents:: Main steps
    :local:
    :depth: 2

.. comment:
    Main steps
    ----------

    * **Import modules**: the first step in any script is to import necessary functions or modules
    * **Define variables**: the definition of variables we use in the script can be put in a separate file (see :ref:`params` for a list of all possible variables)
    * **Specify Nodes**: before to build a Workflow, we have to create some Nodes
    * **Input Stream**: we need to specify the path of the folders where the Workflow can get the data from
    * **Specify Workflows and Connect Nodes**: to set the order in which to execute the just created Nodes, we have to create a Workflow and specify the connections between the Nodes;
    in this way the Workflow will be executed in a sequential mode
    * **Run Workflow**: as last step we can run the Workflow!

    
.. _modules:

Import modules
--------------

The first step is to import the modules we need in the script. We import mainly from nipype and ephypype packages.

.. code:: python

    import os.path as op
    import numpy as np
    import nipype.pipeline.engine as pe
    import json 

    import ephypype
    from ephypype.nodes import create_iterator, create_datagrabber
    from ephypype.datasets import fetch_omega_dataset
    from ephypype.pipelines.power import create_pipeline_power

.. _variables:

Define data and variables
-------------------------

Let us fetch the data first (it is around 675 MB download) and specify some variables that are specific for the data analysis (the main directories where the data are stored,
the list of subjects and sessions, ...) 

.. code:: python  
  
    base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
    data_path = fetch_omega_dataset(base_path)
    
    subject_ids = ['sub-0003']
    session_ids = ['ses-0001']

    
Now we define some variables specific for the pipelines we use (frequency band of interest, method to compute the PSD, ...).
in a :download:`json <https://github.com/neuropycon/ephypype/blob/master/examples/params_power.json>` file and load it in the script. 

.. code-block:: python
    :emphasize-lines: 1

    data = json.load(open("params_power.json"))

    freq_band_names = data['freq_band_names']
    freq_bands = data['freq_bands']
    is_epoched = data['is_epoched']
    fmin = data['fmin']
    fmax = data['fmax']
    power_method = data['method']

Specify Nodes
-------------

Before to create a workflow we have to create the nodes that define the workflow itself. A |node| is an object that can encapsulate 
either an |interface| to an external tool or a **function** defined by the user. A node can also encapsulate an another |workflow|.

.. |node|   raw:: html

    <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_nodes.html" target="_blank">Node</a>
    
.. |interface|   raw:: html

    <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_interfaces.html" target="_blank">Interface</a>
    
.. |workflow|   raw:: html

    <a href="https://miykael.github.io/nipype_tutorial/notebooks/basic_workflow.html" target="_blank">workflow</a>
    
    
    
Every Node has always at least one input and one output field: the knowledge of these inputs and outputs allows to connect the different Nodes
and define the stream of input and output between them. 
In this example the main Nodes are

* ``infosource`` is an IdentityInterface Node that just distributes values (see :ref:`infosource`)
* ``datasource`` is a DataGrabber Node that allows the user to define flexible search patterns which can be parameterized by user defined inputs (see :ref:`datagrabber`)
* ``power_pipeline`` is a Node containing the pipeline created by `create_pipeline_power <https://neuropycon.github.io/ephypype/generated/ephypype.pipelines.create_pipeline_power.html#ephypype.pipelines.create_pipeline_power>`_  (see :ref:`inputnode`)

.. comment: * ``graph_den_pipe_den_0_05`` is a Node containing the pipeline from connectivity matrices to graph analysis created by |create_pipeline_conmat_to_graph_density| (see :ref:`inputnode`)

.. |create_pipeline_conmat_to_graph_density| raw:: html

   <a href="http://davidmeunier79.github.io/graphpype/conmat_to_graph.html#create-pipeline-conmat-to-graph-density" target="_blank">create_pipeline_conmat_to_graph_density</a>

   
.. _infosource:

Infosource
~~~~~~~~~~

The Infosource Node allows to distributes values: when we need to feed the different subject names into the workflow
we only need a Node that can receive the input and distribute those inputs to the workflow. The ephypype function
`create_iterator <https://neuropycon.github.io/ephypype/generated/ephypype.nodes.utils.create_iterator.html#ephypype.nodes.utils.create_iterator>`_ creates this Infosource Node.

.. code:: python

    infosource = create_iterator(['subject_id', 'session_id'], [subject_ids, session_ids])

    
The input fields of infosource node (i.e. ``subject_id``, ``session_id`` ) are defined as iterables.
Iterables are very important for the repeated execution of a workflow with slightly changed parameters.
Indeed, Iterables are used to feed the different subject names into the workflow, and this leads to create 
as many execution workflows as subjects. And depending on your system, all of those workflows could be executed in parallel.

.. comment:
    Iterables are a special kind of input fields and any input field of any Node can be turned into an Iterable. 
    
    In this example script, to run the Workflow for different subjects and sessions we iterate over a list of subject IDs
    and session names by setting the iterables property of the ``datasource`` Node for the inputs ``subject_id`` and ``sess_index``.
    This is performed by connecting these inputs to the iterables inputs of ``infosource`` Node.

.. comment: ``main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')``
.. comment: ``main_workflow.connect(infosource, 'sess_index', datasource, 'sess_index')``

.. _datagrabber:

DataGrabber
~~~~~~~~~~~

The ``DataGrabber Interface`` allows to define flexible search patterns which can be parameterized by user
defined inputs (such as subject ID, session, etc.).
In this example we parameterize the pattern search with ``subject_id`` and ``session_id``. The ephypype function
`create_datagrabber <https://neuropycon.github.io/ephypype/generated/ephypype.nodes.utils.create_datagrabber.html#ephypype.nodes.utils.create_datagrabber>`_ creates a node to grab data using DataGrabber in Nipype.

.. code:: python

    template_path = '*%s/%s/meg/%s*rest*0_60*ica.fif'
    template_args = [['subject_id', 'session_id', 'subject_id']]
    datasource = create_datagrabber(data_path, template_path, template_args)



.. _inputnode:

Pipeline
~~~~~~~~

Each pipeline provided by NeuroPycon requires two different kind of inputs:

* inputs of the pipeline
* **inputnode**: these particular inputs are defined after the creation of the pipeline; an inputnode of a pipeline is defined by an output of a previous Node

For example, looking at the definition of `create_pipeline_power <https://neuropycon.github.io/ephypype/generated/ephypype.pipelines.create_pipeline_power.html#ephypype.pipelines.create_pipeline_power>`_  module
``main_path``, ``freq_bands`` are inputs of the pipeline while ``fif_file`` is an inputnode. In the next section :ref:`workflow` we'll see how to specify this inputnode.

To create the pipeline node we pass the input to the ``create_pipeline_power`` function:

.. code:: python

    power_workflow = create_pipeline_power(data_path, freq_bands, fmin=fmin, fmax=fmax, method=power_method, is_epoched=is_epoched)


.. _workflow:

Specify Workflows and Connect Nodes
-----------------------------------

The purpose of Workflow is to guide the sequential execution of Nodes: we create a main Workflow to connect 
the different Nodes and define the data flow from the outputs of one Node 
to the inputs of the connected Nodes. The specified connections create our workflow: the created nodes and the dependencies
between them are represented as a graph (see :ref:`wf_graph`), in this way it is easy to see which nodes are executed and in 
which order. 

It is important to point out that we have to connect the output and input fields of each node to the output and input fields of another node.
      
First, we create our workflow and specify the `base_dir` which tells nipype the directory in which to store the outputs.


.. code-block:: python
  :emphasize-lines: 4

    power_analysis_name = 'power_workflow'

    main_workflow = pe.Workflow(name=power_analysis_name)
    main_workflow.base_dir = data_path


Then,  we connect the nodes two at a time. First, we connect the two outputs (subject_id and session_id) of the infosource node to the datasource node.
So, these two nodes taken together can grab data.

.. code-block:: python
      
    main_workflow.connect(infosource, 'subject_id', datasource, 'subject_id')
    main_workflow.connect(infosource, 'session_id', datasource, 'session_id')
    
    
Finally, we connect the output of datasource node to the input node of powe pipeline node.

.. code-block:: python
    
    main_workflow.connect(datasource, 'raw_file', power_workflow, 'inputnode.fif_file')

Run Workflow
------------

After we have specified all the nodes and connections of the workflow, the last step is to run it
by calling the ``run()`` method. 
It's also possible to generate static graphs representing nodes and connections between them
by calling ``write_graph()`` method.

If we rerun the workflow, only the nodes whose inputs have changed since the last run
will be executed again.  If not, it will simply return cached results. 
This is achieved by recording a hash of the inputs.

.. code:: python

    # run pipeline:

    main_workflow.write_graph(graph2use='colored')  # colored
    main_workflow.config['execution'] = {'remove_unnecessary_outputs': 'false'}
    main_workflow.run(plugin='MultiProc', plugin_args={'n_procs': 2})

.. _wf_graph:      

.. figure::  ../img/graph.png
    :scale: 75 %
    :align: center
    
    Workflow graph

      
**Download** Json parameters file: :download:`params_power.json <../../examples/params_power.json>`

**Download** Python source code: :download:`plot_power.py <../../examples/plot_power.py>`



