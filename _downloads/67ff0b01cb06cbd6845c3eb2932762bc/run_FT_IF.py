"""
.. _ft_example:

======================================
Compute average regerence on ECoG data
======================================
This scripts shows a very simple example on how to create an Interface wrapping
a desired function of a Matlab toolbox (FieldTrip).

The **input** data should be a **.mat** file containing a data struct accepeted
by FieldTrip
"""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
# License: BSD (3-clause)

# sphinx_gallery_thumbnail_number = 1

import os.path as op

import ephypype
from FT_tools import Reference
from ephypype.datasets import fetch_ieeg_dataset


###############################################################################
# Let us fetch the data first. It is around 675 MB download.

base_path = op.join(op.dirname(ephypype.__file__), '..', 'examples')
data_path = fetch_ieeg_dataset(base_path)

ft_path = '/usr/local/MATLAB/R2018a/toolbox/MEEG/fieldtrip-20200327/'
updatesens = 'no'
refmethod = 'avg'
channels_name = '{\'LPG*\', \'LTG*\'}'


reference_if = Reference()
reference_if.inputs.data_file = op.join(data_path, 'SubjectUCI29_data.mat')
reference_if.inputs.channels = channels_name
reference_if.inputs.ft_path = ft_path
reference_if.inputs.updatesens = updatesens
reference_if.inputs.refmethod = refmethod
reference_if.inputs.script = ''

out = reference_if.run()

print('Rereferenced data saved at {}'.format(out.outputs.data_output))
