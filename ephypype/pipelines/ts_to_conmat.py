"""Wraps spectral connectivity function of MNE, as plot_circular_connectivity.

Author: David Meunier <david_meunier_79@hotmail.fr>
"""
import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface
# ,Function

from ephypype.interfaces.mne.spectral import SpectralConn, PlotSpectralConn
from ephypype.nodes.ts_tools import SplitWindows

# to modify and add in "Nodes"

#from ephypype.spectral import  filter_adj_plot_mat


def create_pipeline_time_series_to_spectral_connectivity(main_path,
                                                         pipeline_name='ts_to_conmat',
                                                         con_method='coh',
                                                         multi_con=False,
                                                         export_to_matlab=False,
                                                         n_windows=[],
                                                         mode='multitaper',
                                                         is_sensor_space=True,
                                                         epoch_window_length=None,
                                                         gathering_method="mean"):
    """
    Description:

        Connectivity pipeline: compute spectral connectivity in a given frequency bands

    Inputs:

        main_path : str
            the main path of the pipeline
        pipeline_name: str (default 'ts_to_conmat')
            name of the pipeline
        con_method : str
            metric computed on time series for connectivity; 
            possible choices: "coh","imcoh","plv","pli","wpli","pli2_unbiased","ppc","cohy","wpli2_debiased"     
        multi_con : bool (default False)
            True if multiple connectivity matrices are exported
        export_to_matlab : bool (default False)
            True if conmat is exported to .mat format as well
        n_windows : list
            list of start and stop points (tuple of two integers) of temporal windows
        mode : str (default 'multipaper')
             mode for computing frequency bands; possible choice: "multitaper","cwt_morlet"
        epoch_window_length : float
             epoched data
        is_sensor_space : bool (default True)
             True if we compute connectivity on sensor space

        gathering_method : str
             how the connectivity matrices are gathered
             possible choices: "mean", "max" or "none": 
             (now a paramter of SpectralConn node)

    Inputs (inputnode):

        ts_file : str
            path to the time series file in .npy format
        freq_band : float
            frequency bands
        sfreq : float
            sampling frequency
        labels_file : str
            path to the file containing a list of labels associated with nodes

    Outputs:

        pipeline : instance of Workflow

    """

    if multi_con:
        pipeline_name = pipeline_name + '_multicon'

    pipeline = pe.Workflow(name=pipeline_name)
    pipeline.base_dir = main_path

    # inputnode = pe.Node(IdentityInterface(fields=['ts_file','freq_band',
    # 'sfreq','labels_file','epoch_window_length','is_sensor_space','index']),
    # name='inputnode')
    fields = ['ts_file', 'sfreq', 'freq_band', 'labels_file']
    inputnode = pe.Node(IdentityInterface(fields=fields), name='inputnode')
    if len(n_windows) == 0:

        print("$$$$$$$$$$$$$$$$$$$$$$$$ Multiple trials $$$$$$$$$$$$$$$$$$$$$")

        # spectral
        spectral = pe.Node(interface=SpectralConn(), name="spectral")

        spectral.inputs.con_method = con_method
        spectral.inputs.export_to_matlab = export_to_matlab
        # spectral.inputs.sfreq = sfreq
        spectral.inputs.multi_con = multi_con
        spectral.inputs.mode = mode
        spectral.inputs.gathering_method = gathering_method

        if epoch_window_length:
            spectral.inputs.epoch_window_length = epoch_window_length

        pipeline.connect(inputnode, 'sfreq', spectral, 'sfreq')
        pipeline.connect(inputnode, 'ts_file', spectral, 'ts_file')
        pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
        # pipeline.connect(inputnode, 'epoch_window_length', spectral,
        # 'epoch_window_length')

        # plot spectral
        if multi_con:
            plot_spectral = pe.MapNode(interface=PlotSpectralConn(
            ), name="plot_spectral", iterfield=['conmat_file'])

            plot_spectral.inputs.is_sensor_space = is_sensor_space
            pipeline.connect(inputnode, 'labels_file',
                             plot_spectral, 'labels_file')
            # pipeline.connect(inputnode,  'is_sensor_space',plot_spectral,
            # 'is_sensor_space')
            pipeline.connect(spectral, "conmat_files",
                             plot_spectral, 'conmat_file')

        else:

            plot_spectral = pe.Node(
                interface=PlotSpectralConn(), name="plot_spectral")

            plot_spectral.inputs.is_sensor_space = is_sensor_space
            pipeline.connect(inputnode, 'labels_file',
                             plot_spectral, 'labels_file')
            # pipeline.connect(inputnode,  'is_sensor_space',plot_spectral,
            # 'is_sensor_space')
            pipeline.connect(spectral, "conmat_file",
                             plot_spectral, 'conmat_file')

    else:

        print("$$$$$$$$$$$$ Multiple windows, multiple trials  $$$$$$$$$$$$$")
        print(n_windows)

        # win_ts
        #####
        win_ts = pe.Node(interface=SplitWindows(), name="win_ts")
        win_ts.inputs.n_windows = n_windows

        pipeline.connect(inputnode, 'ts_file', win_ts, 'ts_file')

        # spectral
        spectral = pe.MapNode(interface=SpectralConn(),
                              name="spectral", iterfield=['ts_file'])

        spectral.inputs.con_method = con_method
        spectral.inputs.export_to_matlab = export_to_matlab
        # spectral.inputs.sfreq = sfreq  # undefined
        spectral.inputs.multi_con = multi_con
        spectral.inputs.mode = mode
        spectral.inputs.epoch_window_length = epoch_window_length
        spectral.inputs.gathering_method = gathering_method

        # pipeline.connect(inputnode, 'sfreq', spectral, 'sfreq')
        pipeline.connect(win_ts, 'win_ts_files', spectral, 'ts_file')
        pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')

        # pipeline.connect(inputnode, 'index', spectral, 'index')
        # pipeline.connect(inputnode, 'epoch_window_length', spectral,
        # 'epoch_window_length')

    return pipeline
