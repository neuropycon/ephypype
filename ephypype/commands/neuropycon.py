"""Command line interface for ephypype package"""

# Authors: Dmitrii Altukhov <daltuhov@hse.ru>
#
# License: BSD (3-clause)

from ..externals import click
import nipype.pipeline.engine as pe
import os


@click.group(chain=True)
@click.option('--ncpu', '-n', default=1, help='number of CPUs to use\
 takes effect only for MultiProc and PBS plugins')
@click.option('--plugin', '-p',
              type=click.Choice(['Linear', 'MultiProc', 'PBS']),
              help='plugin to use; use Linear for single-thread\
 computation, MultiProc for parallel computation on local\
 machine and PBS to compute on cluster',
              default='MultiProc')
@click.option('--save-path', '-s', type=click.Path(), default=os.getcwd(),
              help='path to store results')
@click.option('--workflow-name', '-w', default='my_workflow',
              help='name of destination directory')
@click.option('--verbose/--no-verbose', default=True,
              help='verbosity level')
def cli(ncpu, plugin, save_path, workflow_name, verbose):
    """Parallel processing of MEG/EEG data"""
    output_greeting()


#  ----------------- Connect all the nodes into a workflow ----------------- #
@cli.resultcallback()
def process_pipeline(nodes, ncpu, plugin, save_path, workflow_name, verbose):
    """Create main workflow"""

    input_node, path_node = nodes[-1]

    workflow = pe.Workflow(name=workflow_name)
    workflow.base_dir = (save_path)

    in_out = {'path_node': ('key', 'path'),
              'ep2npy': ('fif_file', 'ts_file'),
              'pwr': ('epochs_file', 'pwr_file'),
              'sp_conn': ('ts_file', 'conmat_file'),
              'mse': ('ts_file', 'mse_file'),
              'ica': ('fif_file', 'ica_file'),
              'preproc': ('fif_file', 'fif_file'),
              'ds2fif': ('ds_file', 'fif_file'),
              'epoching': ('fif_file', 'epo_fif_file')}

    workflow.connect(input_node, 'keys', path_node, 'key')
    prev_node = path_node

    click.echo(click.style(input_node.name.upper(), fg='cyan'), nl=False)

    for node in nodes[:-1]:
        click.secho(' ---> {}'.format(node.name.upper()),
                    fg='cyan', nl=False)

        node.inputs.get()
        workflow.connect(prev_node, in_out[prev_node.name][1],
                         node, in_out[node.name][0])

        prev_node = node
    click.echo()
    if verbose:
        if plugin == 'MultiProc':
            workflow.run(plugin='MultiProc', plugin_args={'n_procs': ncpu})
        elif plugin == 'Linear':
            workflow.run(plugin='Linear')
        elif plugin == 'PBS':
            workflow.run(plugin='PBS')
    else:
        from ..aux_tools import suppress_stdout_stderr
        with suppress_stdout_stderr():
            if plugin == 'MultiProc':
                workflow.run(plugin='MultiProc', plugin_args={'n_procs': ncpu})
            elif plugin == 'Linear':
                workflow.run(plugin='Linear')
            elif plugin == 'PBS':
                workflow.run(plugin='PBS')
# -------------------------------------------------------------------------- #


# ------------------------------- input node ------------------------------- #
@cli.command('input')
@click.argument('fif_files', nargs=-1, type=click.Path(exists=True))
def infosrc(fif_files):
    r"""Specify input.

    Use wildcards to run computations on multiple files;
    To check yourself it's a good idea to run ls command first like this:


    $ ls ./\*/\*.fif

    $ neuropycon <...> input ./\*/\*.fif

    """

    from os.path import abspath, split
    from os.path import commonprefix as cprfx
    from nipype.interfaces.utility import IdentityInterface, Function

    fif_files = [abspath(f) for f in fif_files]

    common_prefix = split(cprfx(fif_files))[0] + '/'
    iter_mapping = dict()
    for fif_file in fif_files:
        new_base = fif_file.replace(common_prefix, '')
        new_base = new_base.replace('/', '__')
        new_base = new_base.replace('.', '-')
        iter_mapping[new_base] = fif_file

    infosource = pe.Node(interface=IdentityInterface(fields=['keys']),
                         name='input')

    path_node = pe.Node(interface=Function(input_names=['key', 'iter_mapping'],
                                           output_names=['path'],
                                           function=map_path),
                        name='path_node')

    infosource.iterables = [('keys', list(iter_mapping.keys()))]
    path_node.inputs.iter_mapping = iter_mapping
    return infosource, path_node
# -------------------------------------------------------------------------- #


# ---------------------- power spectral density node ---------------------- #
@cli.command('psd')
@click.option('--fmin', default=0.,
              help='lower frequency bound; default=0')
@click.option('--fmax', default=300.,
              help='higher frequency bound; default=300')
def psd(fmin, fmax):
    """Compute power spectral density.

    Lower and higher frequency bounds for computation
    can be changed

    Takes as input epochs in .fif format

    EXAMPLE:

    $ neuropycon pwr input ~/fif_epochs/*/*-epo.fif

    """
    from ..interfaces.mne.power import Power
    # click.echo(list(fif_files))
    power = pe.Node(interface=Power(), name='pwr')
    power.inputs.fmin = fmin
    power.inputs.fmax = fmax
    power.inputs.method = 'welch'
    return power
# ------------------------------------------------------------------------- #


# --------------------------- connectivity node --------------------------- #
@cli.command('conn')
@click.option('--band', '-b', nargs=2, type=click.Tuple([float, float]),
              multiple=True, help='frequency band')
@click.option('--method', '-m', nargs=1,
              type=click.Choice(["coh", "imcoh", "plv", "pli",
                                 "wpli", "pli2_unbiased",
                                 "ppc", "cohy", "wpli2_debiased"]),
              default=('imcoh',), multiple=True, help='connectivity measure')
@click.option('--sfreq', '-s', nargs=1, type=click.INT,
              prompt='Input sampling frequency',
              help='data sampling frequency')
@click.option('--tf-mode', '-t', nargs=1,
              type=click.Choice(['multitaper', 'cwt_morlet']),
              default='multitaper',
              help='mode of time-frequency transformation')
def connectivity(band, method, sfreq, tf_mode):
    """Compute spectral connectivity"""

    from ..interfaces.mne.spectral import SpectralConn
    # if not method:
    #     method = ('imcoh',)
    freq_bands = [list(t) for t in band]

    sp_conn = pe.Node(interface=SpectralConn(), name='sp_conn')
    # sp_conn.inputs.con_method = con_method
    sp_conn.inputs.sfreq = sfreq
    sp_conn.inputs.mode = tf_mode
    sp_conn.iterables = [('freq_band', freq_bands), ('con_method', method)]
    return sp_conn
# ------------------------------------------------------------------------- #


# -------------------------- epochs to numpy node -------------------------- #
@cli.command('ep2npy')
def fif_ep_2_ts():
    """Convert .fif epochs to npy timeseries"""

    from ..nodes.import_data import Ep2ts
    ep2ts = pe.Node(interface=Ep2ts(), name='ep2npy')
    return ep2ts
# -------------------------------------------------------------------------- #


# ------------------------ Multiscale entropy node  ------------------------ #
@cli.command('mse')
@click.option('-m', default=2)
@click.option('-r', default=0.2)
def multiscale(m, r):
    """Compute multiscale entropy node

    Experimental functionality.
    Available only in mse branch of ephypype

    """
    from ..mse import get_mse_multiple_sensors
    from nipype.interfaces.utility import Function
    mse = pe.Node(interface=Function(input_names=['ts_file', 'm', 'r'],
                                     output_names=['mse_file'],
                                     function=get_mse_multiple_sensors),
                  name='mse')

    mse.inputs.m = m
    mse.inputs.r = r
    return mse
# -------------------------------------------------------------------------- #


# -------------------------------- ica node -------------------------------- #
@cli.command('ica')
@click.option('--n-components', '-n', default=0.95)
@click.option('--ecg-ch-name', '-c', type=click.STRING, default='')
@click.option('--eog-ch-name', '-o', type=click.STRING, default='')
def ica(n_components, ecg_ch_name, eog_ch_name):
    """Compute ica solution for raw fif file"""
    from ..interfaces.mne.preproc import CompIca
    ica_node = pe.Node(interface=CompIca(), name='ica')
    ica_node.inputs.n_components = n_components
    ica_node.inputs.ecg_ch_name = ecg_ch_name
    ica_node.inputs.eog_ch_name = eog_ch_name
    return ica_node
# -------------------------------------------------------------------------- #


# ------------------------------ Preproc node  ------------------------------ #
@cli.command('preproc')
@click.option('--l-freq', '-l', type=click.FLOAT)
@click.option('--h-freq', '-h', type=click.FLOAT)
@click.option('--ds_freq', '-d', type=click.INT,
              help='downsampling frequency')
def preproc(l_freq, h_freq, ds_freq):
    """Filter and downsample data."""
    from ..interfaces.mne.preproc import PreprocFif

    preproc_node = pe.Node(interface=PreprocFif(), name='preproc')

    if l_freq:
        preproc_node.inputs.l_freq = l_freq
    if h_freq:
        preproc_node.inputs.h_freq = h_freq

    if ds_freq:
        preproc_node.inputs.down_sfreq = ds_freq

    return preproc_node
# --------------------------------------------------------------------------- #


# ------------------------------- ds2fif node ------------------------------- #
@cli.command('ds2fif')
def ds2fif():
    """Convert CTF .ds raw data to .fif format"""
    from ..nodes.import_data import ConvertDs2Fif

    ds2fif_node = pe.Node(interface=ConvertDs2Fif(), name='ds2fif')

    return ds2fif_node
# --------------------------------------------------------------------------- #


# --------------------------- create epochs node --------------------------- #
@cli.command('epoch')
@click.option('--length', '-l', type=click.FLOAT,
              help='epoch length')
def epoch(length):
    """Epoch raw .fif resting state data"""
    from ..interfaces.mne.preproc import CreateEp

    epoch_node = pe.Node(interface=CreateEp(), name='epoching')

    epoch_node.inputs.ep_length = length

    return epoch_node
# -------------------------------------------------------------------------- #


def map_path(key, iter_mapping):
    """Map paths"""
    return iter_mapping[key]


# ------------------------------- Greeting --------------------------------- #
def output_greeting():
    """Output greeting"""

    click.echo(click.style(r'''
  _   _                      _____        _____                 _.-'-'--._
 | \ | |                    |  __ \      / ____|               ,', ~'` ( .'`.
 |  \| | ___ _   _ _ __ ___ | |__) |   _| |     ___  _ __     ( ~'_ , .'(  >-)
 | . ` |/ _ \ | | | '__/ _ \|  ___/ | | | |    / _ \| '_ \   ( .-' (  `__.-<  )
 | |\  |  __/ |_| | | | (_) | |   | |_| | |___| (_) | | | |   ( `-..--'_   .-')
 |_| \_|\___|\__,_|_|  \___/|_|    \__, |\_____\___/|_| |_|    `(_( (-' `-'.-)
                                    __/ |                          `-.__.-'=/
                                   |___/                              `._`='
                                                                        \\
''', fg='magenta'))
