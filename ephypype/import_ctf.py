# -*- coding: utf-8 -*-

import os
import mne

# from mne.io import RawFIF

# mne.set_log_level('WARNING')

import numpy as np

# from params import main_path


# -------------------- nodes (Function)
def convert_ds_to_raw_fif(ds_file):
    """Convert from CTF .ds to .fif and save
    result in pipeline folder structure

    """
    import os
    import os.path as op

    from nipype.utils.filemanip import split_filename as split_f
    from mne.io import read_raw_ctf

    _, basename, ext = split_f(ds_file)
    # print(subj_path, basename, ext)
    raw = read_raw_ctf(ds_file)
    # raw_fif_file = os.path.abspath(basename + "_raw.fif")

    # raw.save(raw_fif_file)
    # return raw_fif_file

    raw_fif_file = os.path.abspath(basename + "_raw.fif")

    if not op.isfile(raw_fif_file):
        raw = read_raw_ctf(ds_file)
        raw.save(raw_fif_file)
    else:
        print('*** RAW FIF file %s exists!!!' % raw_fif_file)
        
    return raw_fif_file


#def convert_ds_to_raw_fif(ds_file):

	#import os

	#from nipype.utils.filemanip import split_filename as split_f

	#subj_path,basename,ext = split_f(ds_file)

	
	##basename = os.path.splitext(ds_file)[0]

	#print subj_path,basename,ext
	##0/0

	#raw_fif_file = os.path.join(subj_path,basename + "_raw.fif")

	#os.system("$MNE_ROOT/bin/mne_ctf2fiff --ds " + os.path.join(subj_path,ds_file) + " --fif " + raw_fif_file)

	#return raw_fif_file


def compute_ROI_coordinates():

    import params_victor as parv
    
        
    label_vertices_victor_file = os.path.join(parv.data_path,"label_vertices_victor.txt")
    
    coord_vertices_victor_file = os.path.join(parv.data_path,"coord_vertices_victor.txt")
    
    coord_vertices_victor =  np.array(np.loadtxt(coord_vertices_victor_file, dtype = 'float'))
    
    print(coord_vertices_victor)
    
    ROI_names = []
    
    ROI_mean_coords = []
    
    with open(label_vertices_victor_file,'r') as f:
        
        lines = f.readlines()
        
        print lines
                
        for i,line in enumerate(lines[1:]):
            
            print line
            
            split_line = line.strip().split(':')
            
            if len(split_line) == 2:
                
                label = split_line[0]
                
                correct_label =  "_".join(label.split(" "))
                
                ROI_names.append(correct_label)
                
                
                print split_line[1].strip().split(' ')
                
                vertex_indexes = np.array(map(int,split_line[1].strip().split(' ')))
                
                print vertex_indexes
                
                np_vertex_indexes = vertex_indexes -1 
                
                print np_vertex_indexes
                
                print coord_vertices_victor[np_vertex_indexes]
                
                mean_coord = np.mean(coord_vertices_victor[np_vertex_indexes,:],axis = 0)
                
                print mean_coord
                
                ROI_mean_coords.append(mean_coord)
                #np_vertice_indexes
            
        print ROI_names
        
        print len(ROI_names)
        
        
        np_ROI_mean_coords = np.array(ROI_mean_coords)
        
        print np_ROI_mean_coords
        
        print np_ROI_mean_coords.shape
        
        np.savetxt(parv.MEG_ROI_coords_file,np_ROI_mean_coords, fmt = "%f")
        
        np.savetxt(parv.MEG_ROI_names_file,np.array(ROI_names,dtype = str), fmt = "%s")

        
# --------------------- testing 
def test_convert_data():
	
	subj_path = os.path.join(main_path ,'balai')

	print(subj_path)

	ds_files = [f for f in os.listdir(subj_path) if f.endswith("ds")]

	print(ds_files)

	for ds_f in ds_files:

		basename = os.path.splitext(ds_f)[0]

		print(basename)

		os.system("$MNE_ROOT/bin/mne_ctf2fiff --ds " + os.path.join(subj_path,ds_f) + " --fif " + os.path.join(subj_path,basename + "_raw.fif"))

		0/0

def test_import_data():
	
	subj_path = os.path.join(main_path ,'balai')

	print(subj_path)

	fif_files = [f for f in os.listdir(subj_path) if f.endswith("fif")]

	print(fif_files)

	for fif_f in fif_files:

		raw = mne.io.Raw(os.path.join(subj_path,fif_f))

		print(raw)

		#print(raw.ch_names)
		#0/0

		print(len(raw.ch_names))

		select_electrodes = np.array([ch_name[0] == 'M' for ch_name in raw.ch_names],dtype = 'bool')

		#print select_electrodes
		#start, stop = raw.time_as_index([0, 100])

		#data,times = raw[:,start:stop]

		data,times = raw[:,:]
		print(data.shape)

		#0/0
		electrode_data = data[select_electrodes,]

		#electrode_data = data[np.where(select_electrodes == True),]

		print(electrode_data.shape)

		basename = os.path.splitext(fif_f)[0]

		np_filename = os.path.join(subj_path,basename + ".npy")

		np.save(np_filename,electrode_data)

		0/0

if __name__ == '__main__':
    	#test_convert_data()
	#test_import_data()

        compute_ROI_coordinates()
        
