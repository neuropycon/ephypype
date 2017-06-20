"""
Description:

Wraps spectral connectivity function of MNE, as well as
plot_circular_connectivity

"""
# Author: David Meunier <david_meunier_79@hotmail.fr>

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import IdentityInterface
#,Function

from ephypype.interfaces.mne.spectral import  SpectralConn,PlotSpectralConn
from ephypype.nodes.ts_tools import SplitWindows

### to modify and add in "Nodes"
#from ephypype.spectral import  filter_adj_plot_mat

def create_pipeline_time_series_to_spectral_connectivity(main_path, 
                                                         pipeline_name='ts_to_conmat',
                                                         con_method='coh',
                                                         multi_con=False,
                                                         export_to_matlab=False,
                                                         n_windows=[],
                                                         mode='multitaper',
                                                         is_sensor_space=True,
                                                         epoch_window_length=None):
    
    """
    Description:

        Connectivity pipeline: compute spectral connectivity in a given frequency bands

    Inputs:

        main_path : str
            the main path of the pipeline
        pipeline_name: str (default 'ts_to_conmat')
            name of the pipeline
        con_method : str
            metric computed on time series for connectivity; possible choice: "coh","imcoh","plv","pli","wpli","pli2_unbiased","ppc","cohy","wpli2_debiased"     
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
        
    pipeline = pe.Workflow(name= pipeline_name)
    pipeline.base_dir = main_path
        
#    inputnode = pe.Node(IdentityInterface(fields=['ts_file','freq_band','sfreq','labels_file','epoch_window_length','is_sensor_space','index']), name='inputnode')
    inputnode = pe.Node(IdentityInterface(fields=['ts_file', 'freq_band',
                                                  'sfreq', 'labels_file']), name='inputnode')
    if len(n_windows) == 0:
            
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Multiple trials $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        
        #### spectral
        spectral = pe.Node(interface = SpectralConn(), name = "spectral")
        
        spectral.inputs.con_method = con_method  
        spectral.inputs.export_to_matlab = export_to_matlab
        #spectral.inputs.sfreq = sfreq
        spectral.inputs.multi_con = multi_con
        spectral.inputs.mode = mode
        if epoch_window_length:
            spectral.inputs.epoch_window_length = epoch_window_length
        
        pipeline.connect(inputnode, 'sfreq', spectral, 'sfreq')
        pipeline.connect(inputnode, 'ts_file', spectral, 'ts_file')
        pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
#        pipeline.connect(inputnode, 'epoch_window_length', spectral, 'epoch_window_length')

        #### plot spectral
        if multi_con:
            plot_spectral = pe.MapNode(interface = PlotSpectralConn(), name = "plot_spectral",iterfield = ['conmat_file'])
            
            plot_spectral.inputs.is_sensor_space = is_sensor_space        
            pipeline.connect(inputnode,  'labels_file',plot_spectral,'labels_file')
    #        pipeline.connect(inputnode,  'is_sensor_space',plot_spectral,'is_sensor_space')        
            pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
            
        else:
            
            plot_spectral = pe.Node(interface = PlotSpectralConn(), name = "plot_spectral")
            
            plot_spectral.inputs.is_sensor_space = is_sensor_space        
            pipeline.connect(inputnode,  'labels_file',plot_spectral,'labels_file')
    #        pipeline.connect(inputnode,  'is_sensor_space',plot_spectral,'is_sensor_space')        
            pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
        
        
    else:
        
        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Multiple windows, multiple trials  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        print n_windows
        
        ### win_ts
        ##### 
        win_ts = pe.Node(interface = SplitWindows(), name = "win_ts")            
        win_ts.inputs.n_windows = n_windows
        
        pipeline.connect(inputnode, 'ts_file', win_ts, 'ts_file')

        
        #### spectral
        spectral = pe.MapNode(interface = SpectralConn(), name = "spectral",iterfield = ['ts_file'])
        
        spectral.inputs.con_method = con_method  
        spectral.inputs.export_to_matlab = export_to_matlab            
        #spectral.inputs.sfreq = sfreq
        spectral.inputs.multi_con = multi_con
        spectral.inputs.mode = mode
        spectral.inputs.epoch_window_length = epoch_window_length
        
        pipeline.connect(inputnode, 'sfreq', spectral, 'sfreq')
        pipeline.connect(win_ts, 'win_ts_files', spectral, 'ts_file')
        pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
        
        #pipeline.connect(inputnode, 'index', spectral, 'index')
        #pipeline.connect(inputnode, 'epoch_window_length', spectral, 'epoch_window_length')

    return pipeline
    
    
    
    
    
    
    
    
    
    
#### previous version in vhdr 
    #if multicon == False:
        
        #if len(n_windows) == 0:
                
            ##### spectral
            #spectral = pe.Node(interface = SpectralConn(), name = "spectral")
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            #pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
            #pipeline.connect(split_vhdr, 'splitted_ts_file', spectral, 'ts_file')

            ##### plot spectral
            #plot_spectral = pe.Node(interface = PlotSpectralConn(), name = "plot_spectral")
            
            #pipeline.connect(split_vhdr,  'channel_names',plot_spectral,'labels_file')
            #pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
            
            
            ##if filter_spectral == True:
                    
                ##### filter spectral
                ##filter_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","sep_label_name","k_neigh"], 
                                                            ##output_names = "filtered_conmat_file", 
                                                            ##function = filter_adj_plot_mat), name = "filter_spectral_" + str(k_neigh))
                ##filter_spectral.inputs.sep_label_name = sep_label_name
                ##filter_spectral.inputs.k_neigh = k_neigh
                
                ##pipeline.connect(split_vhdr,  'channel_names',filter_spectral,'labels_file')
                ##pipeline.connect(spectral, "conmat_file",    filter_spectral, 'conmat_file')
                
                
                
                ###### plot filter_spectral
                ##plot_filter_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","nb_lines","vmin","vmax"],
                                                            ##output_names = "plot_conmat_file",
                                                            ##function = plot_circular_connectivity), name = "plot_filter_spectral_" + str(k_neigh))
                
                ### plot_spectral.inputs.labels_file = MEG_elec_names_file AP 021015
                ##plot_filter_spectral.inputs.nb_lines = 50
                
                ##plot_filter_spectral.inputs.vmin = 0.3
                ##plot_filter_spectral.inputs.vmax = 1.0
            
            
                ##pipeline.connect(split_vhdr,  'channel_names',plot_filter_spectral,'labels_file')
                ##pipeline.connect(filter_spectral, "filtered_conmat_file",    plot_filter_spectral, 'conmat_file')
                
        #else:
            
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Multiple windows $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print n_windows
            
            #### win_ts
            #win_ts = pe.Node(interface = SplitWindows(), name = "win_ts")
            
            #win_ts.inputs.n_windows = n_windows
            
            #pipeline.connect(split_vhdr, 'splitted_ts_file', win_ts, 'ts_file')

            ##### spectral
            #spectral = pe.MapNode(interface = SpectralConn(), iterfield = ['ts_file'], name = "spectral")
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            ##spectral.inputs.epoch_window_length = epoch_window_length
            #pipeline.connect(win_ts, 'win_ts_files', spectral, 'ts_file')
            #pipeline.connect(inputnode,'freq_band', spectral, 'freq_band')
            
            
            ##### plot spectral
            ##plot_spectral = pe.MapNode(interface = PlotSpectralConn(), name = "plot_spectral")
            
            ###plot_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","nb_lines","vmin","vmax"],
                                                        ###output_names = "plot_conmat_file",
                                                        ###function = plot_circular_connectivity), name = "plot_spectral")
            
            ### plot_spectral.inputs.labels_file = MEG_elec_names_file AP 021015
            ##plot_spectral.inputs.nb_lines = 200
            ##plot_spectral.inputs.vmin = 0.3
            ##plot_spectral.inputs.vmax = 1.0
            
            ##pipeline.connect(split_vhdr,  'channel_names',plot_spectral,'labels_file')
            ##pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
            
    #else:
        #if len(n_windows) == 0:
                
            ##### spectral
            #spectral = pe.Node(interface = Function(input_names = ["ts_file","sfreq","freq_band","con_method"],
                                                    #output_names = "conmat_files",
                                                    #function = multiple_spectral_proc),name = "spectral")
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            #pipeline.connect(split_ascii, 'splitted_ts_file', spectral, 'ts_file')
            #pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
            
        #else:
            
            #print "$$$$$$$$$$$$$$$$$$$$$$$ Multiple windows, multiple connectivity  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print n_windows
            
            #### win_ts
            ###### 
            #win_ts = pe.Node(interface = SplitWindows(), name = "win_ts")
            
            #win_ts.inputs.n_windows = n_windows
            
            #pipeline.connect(split_vhdr, 'splitted_ts_file', win_ts, 'ts_file')

            ##### spectral
            #spectral = pe.MapNode(interface = Function(input_names = ["ts_file","sfreq","freq_band","con_method"],
                                                    #output_names = "conmat_files",
                                                    #function = multiple_spectral_proc),name = "spectral",iterfield = ['ts_file'])
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            #pipeline.connect(win_ts, 'win_ts_files', spectral, 'ts_file')
            #pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
            
            
            ###### plot spectral
            ##plot_spectral = pe.MapNode(interface = PlotSpectralConn(), name = "plot_spectral")
            
            ###plot_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","nb_lines","vmin","vmax"],
                                                        ###output_names = "plot_conmat_file",
                                                        ###function = plot_circular_connectivity), name = "plot_spectral")
            
            ### plot_spectral.inputs.labels_file = MEG_elec_names_file AP 021015
            ##plot_spectral.inputs.nb_lines = 200
            ##plot_spectral.inputs.vmin = 0.3
            ##plot_spectral.inputs.vmax = 1.0
            
            ##pipeline.connect(split_vhdr,  'channel_names',plot_spectral,'labels_file')
            ##pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
           
    
### previous version, was in split_ascii

     
    #if multicon == False:
        
        #if len(n_windows) == 0:
                
            ##### spectral
            
            #spectral = pe.Node(interface = SpectralConn(), name = "spectral")
            
            ##spectral = pe.Node(interface = Function(input_names = ["ts_file","sfreq","freq_band","con_method"],
            ##                                        output_names = "conmat_file",
            ##                                        function = spectral_proc),name = "spectral")
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            #pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')
            
            #pipeline.connect(split_ascii, 'splitted_ts_file', spectral, 'ts_file')

            ##### plot spectral
            #plot_spectral = pe.Node(interface = PlotSpectralConn(), name = "plot_spectral")
            
            ##plot_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","nb_lines","vmin","vmax"],
                                                        ##output_names = "plot_conmat_file",
                                                        ##function = plot_circular_connectivity), name = "plot_spectral")
            
            ## plot_spectral.inputs.labels_file = MEG_elec_names_file AP 021015
            #plot_spectral.inputs.nb_lines = 200
            #plot_spectral.inputs.vmin = 0.3
            #plot_spectral.inputs.vmax = 1.0
            
            #pipeline.connect(split_ascii,  'elec_names_file',plot_spectral,'labels_file')
            #pipeline.connect(spectral, "conmat_file",    plot_spectral, 'conmat_file')
            
            
            ##if filter_spectral == True:
                    
                ##### filter spectral
                ##filter_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","sep_label_name","k_neigh"], 
                                                            ##output_names = "filtered_conmat_file", 
                                                            ##function = filter_adj_plot_mat), name = "filter_spectral_" + str(k_neigh))
                ##filter_spectral.inputs.sep_label_name = sep_label_name
                ##filter_spectral.inputs.k_neigh = k_neigh
                
                ##pipeline.connect(split_ascii,  'elec_names_file',filter_spectral,'labels_file')
                ##pipeline.connect(spectral, "conmat_file",    filter_spectral, 'conmat_file')
                
                
                
                ###### plot filter_spectral
                ##plot_filter_spectral = pe.Node(interface = Function(input_names = ["conmat_file","labels_file","nb_lines","vmin","vmax"],
                                                            ##output_names = "plot_conmat_file",
                                                            ##function = plot_circular_connectivity), name = "plot_filter_spectral_" + str(k_neigh))
                
                ### plot_spectral.inputs.labels_file = MEG_elec_names_file AP 021015
                ##plot_filter_spectral.inputs.nb_lines = 50
                
                ##plot_filter_spectral.inputs.vmin = 0.3
                ##plot_filter_spectral.inputs.vmax = 1.0
            
            
                ##pipeline.connect(split_ascii,  'elec_names_file',plot_filter_spectral,'labels_file')
                ##pipeline.connect(filter_spectral, "filtered_conmat_file",    plot_filter_spectral, 'conmat_file')
                
        #else:
            #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Multiple windows $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            #print n_windows
            
            #### win_ts
            ###### 
            #win_ts = pe.Node(interface = SplitWindows(), name = "win_ts")
            
            #win_ts.inputs.n_windows = n_windows
            
            #pipeline.connect(split_vhdr,'splitted_ts_file',win_ts,'ts_file')
                    
            ##win_ts = pe.Node(interface = Function(input_names = ["splitted_ts_file","n_windows"],output_names = ["win_splitted_ts_files"],function = split_win_ts), name = "win_ts")
            
            ##win_ts.inputs.n_windows = n_windows
            
            ##pipeline.connect(split_ascii,'splitted_ts_file',win_ts,'splitted_ts_file')
                    
                    
            #spectral = pe.MapNode(interface = SpectralConn(), iterfield = ['ts_file'], name = "spectral")
            
            
            #spectral.inputs.con_method = con_method    
            #spectral.inputs.sfreq = sfreq
            
            ##spectral.inputs.epoch_window_length = epoch_window_length
            #pipeline.connect(win_ts, 'win_ts_files', spectral, 'ts_file')
            #pipeline.connect(inputnode,'freq_band', spectral, 'freq_band')
    #else:
        
        ##### spectral
        #spectral = pe.Node(interface = Function(input_names = ["ts_file","sfreq","freq_band","con_method"],
                                                #output_names = "conmat_files",
                                                #function = multiple_spectral_proc),name = "spectral")
        
        #spectral.inputs.con_method = con_method    
        #spectral.inputs.sfreq = sfreq
        
        #pipeline.connect(split_ascii, 'splitted_ts_file', spectral, 'ts_file')
        #pipeline.connect(inputnode, 'freq_band', spectral, 'freq_band')

    
    