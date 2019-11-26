Tutorial
========

Core idea behind neuropycon_cli is to make use of wildcards provided
by UNIX shell to handle datasets with nested folders organization so the target
files can be processed in parallel and so the results can be stored in
a folder structure identical to the original one.

In this section I will explain, how to combine neuropycon_cli
commands to join data processing nodes into pipelines and how
to select input files from dataset folders in the most efficient way using wildcards.


Commands, options and arguments
-------------------------------

In each call to *neuropycon command line* interface we aim to
build a processing pipeline or a **workflow**. Namely, we specify which processing nodes
we want to run on the data, how we want to connect them and how we want the
resulting pipeline to be run.

For each processing node there's a corresponding **command** in the command line interface.
To specify how a particular node should be invoked, we use **options** to these commands.

To illustrate this let's start with the command that is always
going to appear first --- :code:`neuropycon`.
This command has several options defining the general behaviour of the pipeline.
For instance, :code:`-p` or :code:`--plugin` option defines weither the workflow should
be run in parallel or serial fashion. Another option, :code:`-n` or :code:`--ncpu` defines
how many parallel threads should be used.
Thus, if we want our workflow to run in parallel on 4 cores, we should start with

.. code:: bash

    $ neuropycon -p MultiProc -n 4 <...>


Probably the most useful option for the start is :code:`--help`
which shows a help message with a full list of
available commands and options and exits.
This option can be used on any command to see what it does and what options can/must be set.
Try for instance

.. code:: bash

    $ neuropycon --help

or

.. code:: bash

    $ neuropycon ica --help

Options to neuropycon commands always start with single or double hyphen depending on
weither the short or long option name is used (i.e. :code:`-n` and :code:`--ncpu` options for
neuropycon command). Most of the time options are not required to be set explicitly since
most of them have default values. If no default value is set for an option and user does not set
such option explicitly the prompt with a demand to set an option will appear.

In contrast to options, **arguments** specification in neuropycon_cli is mandatory and
is used only for :code:`input` command which (don't look surprized) specifies paths to the input files.
The number of arguments to **input** command is unlimited
and each argument should go as is (without hyphens). Arguments should be separated by whitespaces.

For example, imagine we had two files named :code:`sample1.fif` and :code:`sample2.fif` in the current working directory.
You can create two empty files for testing purposes by running

.. code:: bash

    $ touch sample1.fif sample2.fif


The most simple looking pipeline would look like

.. code:: bash

   $ neuropycon input sample1.fif sample2.fif

     _   _                      _____        _____                 _.-'-'--._
    | \ | |                    |  __ \      / ____|               ,', ~'` ( .'`.
    |  \| | ___ _   _ _ __ ___ | |__) |   _| |     ___  _ __     ( ~'_ , .'(  >-)
    | . ` |/ _ \ | | | '__/ _ \|  ___/ | | | |    / _ \| '_ \   ( .-' (  `__.-<  )
    | |\  |  __/ |_| | | | (_) | |   | |_| | |___| (_) | | | |   ( `-..--'_   .-')
    |_| \_|\___|\__,_|_|  \___/|_|    \__, |\_____\___/|_| |_|    `(_( (-' `-'.-)
                                       __/ |                          `-.__.-'=/
                                      |___/                              `._`='
                                                                           \\
    180108-16:24:35,776 workflow INFO:
             Workflow my_workflow settings: ['check', 'execution', 'logging']
    180108-16:24:35,780 workflow INFO:
             Running in parallel.
    180108-16:24:35,781 workflow INFO:
             Executing: path_node.a1 ID: 0
    180108-16:24:35,783 workflow INFO:
             Executing node path_node.a1 in dir: /home/dmalt/my_workflow/_keys_sample2-fif/path_node
    180108-16:24:35,790 workflow INFO:
             [Job finished] jobname: path_node.a1 jobid: 0
    180108-16:24:35,791 workflow INFO:
             Executing: path_node.a0 ID: 1
    180108-16:24:35,793 workflow INFO:
             Executing node path_node.a0 in dir: /home/dmalt/my_workflow/_keys_sample1-fif/path_node
    180108-16:24:35,796 workflow INFO:
             [Job finished] jobname: path_node.a0 jobid: 1



This pipeline does pretty much nothing since we didn't
specify commands including any processing nodes.
The only result would be appearance in the current working directory of
a folder named :code:`my_workflow` with some logging information
and subfolder :code:`_keys_sample-fif` named so to uniquely correspond to the file
being processed.
If we were actually doing some useful job all the result would appear inside the
:code:`_keys_sample-fif` folder.


Commands order
--------------

Now let's add more nodes to the pipeline.

To do so two rules must be followed concerning the order of invoked commands.

1. :code:`input` command must always appear **last**.
   This limitation allows specifying input without knowing in advance the exact
   number of files to be processed,
   i.e. when we take all files matching  a `wildcard` (see below).
2. All nodes corresponding to the commands other than :code:`input` are linked in
   order of appearance. Output from the previous node becomes an input of the next.

In practice this means that  i) order of commands matters, ii) input and output of adjacent nodes
must be coherent and iii) no matter what, input specification must always be the last thing in the
chain of commands.

For example, suppose we had :code:`resting_state.fif` file with resting state MEG data
and we want to cut it into 1-second epochs and save these epochs in numpy format :code:`.npy`.
Sequence of nodes for this task should look as following:

.. figure::  ./img/nodes_order.png
   :align:   center

Having in mind rules outlined above we can write the corresponding sequence of commands:

.. code:: bash

    $ neuropycon epoch -l 1 ep2npy input resting_state.fif

:code:`-l 1` option defines the resulting epochs to be of 1 second length.

Input specification
-------------------

A common scenario for MEEG datasets organization would be when
the recorded data for a number of subjects are stored in subfolders
with each subfolder's name depicting information about subject's number,
recording condition, applied preprocessing steps etc.

Sample folders layout might look as following:

.. include:: folders_layout.txt
   :literal:

Here we have 5 subjects with subject IDs K0015, K0025, K0034, R0008, R0023.
For each of them there are two :code:`.fif` files with MEG recordings for eyes closed
and eyes open conditions.

One way to go about the processing of these data would be to manually deal
with each file we want to process which isn't very handy for big datasets.

A better idea would be to make use of a regular organization of subfolders.
Normally dataset processing requires applying a set of operations to similar files
inside the folders tree and it would be nice if we could address these subgroups of
similar files using some kind of matching patterns to apply a certain pipeline
of processing operations to them. A perfect tool for that is provided by
UNIX shell.

Consider the following example:

If we were to list all the fif files in the subdirectories
we could use a shell command like this:

.. code:: bash

    $ ls ./NeuroPyConData/*/*.fif

Where * symbol is a `wildcard`_ mapping one or more string literals.

.. _wildcard: https://ryanstutorials.net/linuxtutorial/wildcards.php

Now if we wanted to list only those files that contain recordings for
the 'eyes closed' conditiion we would go like this:

.. code:: bash

    $ ls ./NeuroPyConData/*/*ec.fif

Note 'ec' suffix et the end of our matching pattern.

Similar syntax can be applied if we want to process matching files instead of just listing them.

Let's proceed with the example from the previous section where we epoched a single file
and converted it to :code:`.npy` format. To apply processing steps to all eyes-closed
files in our dataset all we have to do is use the wildcard we've already created:

.. code:: bash

    $ neuropycon epoch -l 1 ep2npy input ./NeuroPyConData/*/*ec.fif

      _   _                      _____        _____                 _.-'-'--._
     | \ | |                    |  __ \      / ____|               ,', ~'` ( .'`.
     |  \| | ___ _   _ _ __ ___ | |__) |   _| |     ___  _ __     ( ~'_ , .'(  >-)
     | . ` |/ _ \ | | | '__/ _ \|  ___/ | | | |    / _ \| '_ \   ( .-' (  `__.-<  )
     | |\  |  __/ |_| | | | (_) | |   | |_| | |___| (_) | | | |   ( `-..--'_   .-')
     |_| \_|\___|\__,_|_|  \___/|_|    \__, |\_____\___/|_| |_|    `(_( (-' `-'.-)
                                        __/ |                          `-.__.-'=/
                                       |___/                              `._`='
                                                                            \\
    INPUT ---> EPOCHING ---> EP2NPY
    180109-18:28:11,91 workflow INFO:
             Workflow my_workflow settings: ['check', 'execution', 'logging']
    180109-18:28:11,99 workflow INFO:
             Running in parallel.
    180109-18:28:11,101 workflow INFO:
             Executing: path_node.a4 ID: 0
    180109-18:28:11,103 workflow INFO:
    ...
    ...
    ...

As we can see from the output just below the NeuroPyCon logo,
the created pipeline is indeed input ---> epoching ---> ep2npy.

Generated output
----------------

After running the line above a newly created folder named :code:`my_workflow` will appear
in the current working directory.

.. hint:: We can change the default name and location of the output
         folder from :code:`./my_workflow` by specifying options :code:`--save-path` or :code:`-s`
         and :code:`--workflow-name` or :code:`-w`
         to :code:`neuropycon` command like this:

         .. code:: bash

            $ neuropycon -s ~/ -w npy_convert_workflow epoch -l 1 ep2npy input ./NeuroPyConData/*/*ec.fif


Let's explore the contents of this directory

.. code:: bash

    $ ls my_workflow
    d3.js
    graph1.json
    graph.json
    index.html
    _keys_K0015__K0015_rest_raw_tsss_mc_trans_ec-fif
    _keys_K0025__K0025_rest_raw_tsss_mc_trans_ec-fif
    _keys_K0034__K0034_rest_raw_tsss_mc_trans_ec-fif
    _keys_R0008__R0008_rest_raw_tsss_mc_trans_ec-fif
    _keys_R0023__R0023_rest_raw_tsss_mc_trans_ec-fif

We see that there are 4 folders starting with :code:`_keys_<SubjID>__` --- one  for each of the files
processed. Let's look inside one of them:

.. code::

    _keys_K0015__K0015_rest_raw_tsss_mc_trans_ec-fif
    ├── ep2npy
    │   ├── _0x3ea00ae5c1c4233082317a7027820486.json
    │   ├── _inputs.pklz
    │   ├── _node.pklz
    │   ├── _report
    │   │   └── report.rst
    │   ├── result_ep2npy.pklz
    │   └── ts_epochs.npy
    ├── epoching
    │   ├── _0x78142f3fd848accc85737102606876da.json
    │   ├── _inputs.pklz
    │   ├── K0015_rest_raw_tsss_mc_trans_ec-epo.fif
    │   ├── _node.pklz
    │   ├── _report
    │   │   └── report.rst
    │   └── result_epoching.pklz
    └── path_node
        ├── _0x32a93e6b5a92f59c1ebfc1e1347577b4.json
        ├── _inputs.pklz
        ├── _node.pklz
        ├── _report
        │   └── report.rst
        └── result_path_node.pklz

Thus, each of the processing nodes created a folder in the outuput directory except for
the :code:`input` node (instead there's path_node folder which is required for inner machinery of the
CLI to work)
Inside the :code:`ep2npy` folder we can find :code:`ts_epochs.npy` file with numpy-converted epoched
data.
:code:`epoching` folder has :code:`K0015_rest_raw_tsss_mc_trans_ec-epo.fif` --- file with `MNE-python
Epochs <https://martinos.org/mne/stable/generated/mne.Epochs.html#mne.Epochs>`__ data structure.

These are the main outputs of the pipeline we just applied to our data.
These files can be used for further and analyses
(i.e. used as input for another :code:`neuropycon` chain of commands).

The rest of files in these folders contains **caching** files  and logging information for the executed
nodes. You can read about them in `nipype documentation <http://nipype.readthedocs.io/en/latest/>`__.
Some hint about caching and how it can be useful though will be given in the next section.

Hotstart
--------

Nipype framework around which neuropycon_cli is built is smart about re-running computations.
As I've already pointed out some caching information is stored inside the output directory.
It means that if we were to rerun the pipeline with the same input again `nipype`  would
use this information together with the output files and it would understand that
certain nodes have already been executed and it would not run them again.

Now imagine that after converting the data to numpy we realized that it would also be useful
to look at some connectivity measure (i.e. imaginary part of coherency) on these data.
We could just use good and ready :code:`.npy` files from the
:code:`ep2npy` subfolders
and supply them as an input to another :code:`neruopycon ...` chain which will create yet another
(or overwrite existing) output folder with the connectivity matrices inside.

This is a bit messy though.
A cleaner way would be to make use of the caching capabilities of `nipype`.
We can simply augment our previous command-chain with
a new :code:`conn` command and it will automatically pick up outputs from the precomputed nodes
and use them for connectivity computation. The result will look as following:

.. code:: bash

    $ neuropycon  epoch -l 1 ep2npy conn -b 8 12 -s 1000 input NeuroPyConData/*/*ec.fif

And if we looked again inside the :code:`_keys_K0015__K0015_rest_raw_tsss_mc_trans_ec` folder
we would see that a new folder with connectivity matrix in :code:`.npy` indeed appeared inside :

.. code::

    _keys_K0015__K0015_rest_raw_tsss_mc_trans_ec-fif
    ├── _con_method_imcoh_freq_band_8.0.12.0
    │   └── sp_conn
    │       ├── _0x289b2f9a3344b8cc2f8cb32978d83319.json
    │       ├── conmat_0_imcoh.npy
    │       ├── _inputs.pklz
    │       ├── _node.pklz
    │       ├── _report
    │       │   └── report.rst
    │       └── result_sp_conn.pklz
    ├── ep2npy
    │   ├── _0xc93cf8c735df05d156d881d7026c399c.json
    │   ├── _inputs.pklz
    │   ├── _node.pklz
    │   ├── _report
    │   │   └── report.rst
    │   ├── result_ep2npy.pklz
    │   └── ts_epochs.npy
    ├── epoching
    │   ├── _0x78142f3fd848accc85737102606876da.json
    │   ├── _inputs.pklz
    │   ├── K0015_rest_raw_tsss_mc_trans_ec-epo.fif
    │   ├── _node.pklz
    │   ├── _report
    │   │   └── report.rst
    │   └── result_epoching.pklz
    └── path_node
        ├── _0x32a93e6b5a92f59c1ebfc1e1347577b4.json
        ├── _inputs.pklz
        ├── _node.pklz
        ├── _report
        │   └── report.rst
        └── result_path_node.pklz
