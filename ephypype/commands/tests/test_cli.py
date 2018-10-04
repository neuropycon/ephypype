"""Test neuropycon command line interface"""

# Authors: Dmitrii Altukhov <daltuhov@hse.ru>
#
# License: BSD (3-clause)


import os
import os.path as op
from ephypype.commands import neuropycon
from click.testing import CliRunner

import matplotlib
matplotlib.use('Agg')  # for testing don't use X server


def test_input_linear():
    """Test input node with Linear plugin (serial workflow execution)"""
    runner = CliRunner()
    wf_name = 'test_input_linear'
    with runner.isolated_filesystem():
        with open('temp.fif', 'w') as f:
            f.write('temp')
        result = runner.invoke(neuropycon.cli, ['-s', os.getcwd(),
                                                '-w', wf_name,
                                                'input', 'temp.fif'])
        assert result.exit_code == 0
        assert os.path.exists(op.join(os.getcwd(), wf_name))


def test_input_multiproc():
    """Test input node with MultiProc plugin (parallel workflow execution)"""
    runner = CliRunner()
    wf_name = 'test_input_multiproc'
    with runner.isolated_filesystem():
        with open('temp.fif', 'w') as f:
            f.write('temp')
        result = runner.invoke(neuropycon.cli, ['-s', os.getcwd(),
                                                '-w', wf_name,
                                                '-p', 'MultiProc',
                                                'input', 'temp.fif'])
        assert result.exit_code == 0
        assert os.path.exists(op.join(os.getcwd(), wf_name))
