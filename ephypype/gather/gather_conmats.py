
import re

import itertools as iter
import numpy as np

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

    
def return_full_mat(mat,elec_labels,all_elec_labels):
    
    print mat
    
    print elec_labels
    
    assert len(mat.shape) == 2 and mat.shape[0] == mat.shape[1], "Error mat shape = {} should be a 2D squared ndarray (matrix)".format(mat.shape)
    assert len(elec_labels) == mat.shape[0] and len(elec_labels) == mat.shape[1] , "Error, both mat dimension {} {} should be the same as elec_labels {}".format(mat.shape[0],mat.shape[1],len(elec_labels))
    
    
    ### if undirected (values are not the same on both triangular parts
    if np.sum(mat[np.tril_indices(mat.shape[0],k =-1)]) != np.sum(mat[np.triu_indices(mat.shape[0],k =1)]):
    #if np.sum(mat[np.tril_indices(mat.shape,k =-1)]) == 0.0 and np.sum(mat[np.triu_indices(mat.shape,k =1)]) != 0.0:
    
        mat = mat + np.transpose(mat)
    
    #### building full_mat from all_elec_labels
    print all_elec_labels
    
    full_mat = np.empty((len(all_elec_labels),len(all_elec_labels)))
    full_mat[:] = np.NAN
    
    for pair_lab in permutations(all_elec_labels,2):
        
        all_i,all_j =  all_elec_labels.index(pair_lab[0]),all_elec_labels.index(pair_lab[1])
             
        if pair_lab[0] in elec_labels and pair_lab[1] in elec_labels:
            
             i,j =  elec_labels.index(pair_lab[0]),elec_labels.index(pair_lab[1])
             
             full_mat[all_i,all_j] = mat[i,j]
             
    print full_mat
    
    return full_mat
    
    
    