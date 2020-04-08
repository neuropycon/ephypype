"""
.. _ft_seeg_example:

=========================================
Apply bipolar montage to depth electrodes
=========================================
This scripts shows a very simple example on how to create an Interface wrapping
a desired function of a Matlab toolbox (|FieldTrip|).

.. |FieldTrip| raw:: html

    <a href="http://www.fieldtriptoolbox.org/" target="_blank">FieldTrip</a>

The **input** data should be a **.mat** file containing a FieldTrip data struct
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

import os.path as op

import ephypype
from ephypype.nodes.FT_tools import Reference
from ephypype.datasets import fetch_ieeg_dataset


###############################################################################
# Let us fetch the data first. It is around 675 MB download.

base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_ieeg_dataset(base_path)

ft_path = '/usr/local/MATLAB/R2018a/toolbox/MEEG/fieldtrip-20200327/'
refmethod = 'bipolar'
channels_name = '{\'RAM*\', \'RHH*\', \'RTH*\', \'ROC*\', \'LAM*\',\'LHH*\', \'LTH*\'}'  # noqa


reference_if = Reference()
reference_if.inputs.data_file = op.join(data_path, 'SubjectUCI29_data.mat')
reference_if.inputs.channels = channels_name
reference_if.inputs.ft_path = ft_path
reference_if.inputs.refmethod = refmethod
reference_if.inputs.script = ''

out = reference_if.run()

print('Rereferenced data saved at {}'.format(out.outputs.data_output))
