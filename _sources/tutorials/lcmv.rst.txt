.. _lcmv:

   
How to add MNE function to ephypype
===================================

The following section is a brief introduction on how to add to **ephypype** a new pipeline based on an algorithm already implemented in the software wrapped by NeuroPycon (e.g. MNE python, radatools).

Here, we add a source reconstruction pipeline using a Linear Constrained Minimum Variance (LCMV) beamformer (Van Veen et al., 1997) as inverse method (see :ref:`LCMV_source_reconstruction` Section).
This will lead to modify only the ephypype package by writing very few lines of code (almost 10).


.. comments
    Main steps
    ----------

    * **Pipeline Input**: allow as input a new inverse method
    * **Interface**: modify the run function
    * **Function**: create a new function

.. contents:: Main steps
    :local:
    :depth: 2
    

.. _pipeline:

Pipeline Input
^^^^^^^^^^^^^^

We can use the same example script of the :download:`inverse solution pipeline <https://github.com/neuropycon/ephypype/blob/master/examples/plot_inverse.py>`. 
The only thing to change is the ``method`` parameter in the :download:`json <https://github.com/neuropycon/ephypype/blob/master/examples/params_LCMV_inverse.json>` file. 

.. code-block:: python
  :emphasize-lines: 4
  
  {
    "spacing": "oct-6",
    "snr": 1.0,
    "method": "LCMV",
    "parcellation": "aparc",
    "noise_cov_fname": "*noise*.ds"
  }
  
.. _interface:

Modify Interface
^^^^^^^^^^^^^^^^

Now, we modify the ``_run_interface`` method of the `Inverse_solution <https://github.com/neuropycon/ephypype/blob/master/ephypype/interfaces/mne/Inverse_solution.py>`_  Interface
by adding the new function ``_compute_LCMV_inverse_solution``

.. code-block:: python  
  
    self.ts_file, self.labels, self.label_names, self.label_coords = \
        _compute_LCMV_inverse_solution(raw_filename, sbj_id, subjects_dir, fwd_filename, cov_filename,
                                        parc=parc, all_src_space=all_src_space, ROIs_mean=ROIs_mean, is_fixed=is_fixed)

                                        
.. _function:

Add Function
^^^^^^^^^^^^

Finally, we include in the module `compute_inv_problem.py <https://github.com/neuropycon/ephypype/blob/master/ephypype/compute_inv_problem.py>`_ the new function 
``_compute_LCMV_inverse_solution`` that calls the MNE python functions (|make_lcmv|, |apply_lcmv_raw|) we have to use to reconstruct the neural activity by an LCMV beamformer starting from raw data.



.. |make_lcmv| raw:: html

   <a href="https://mne.tools/stable/generated/mne.beamformer.make_lcmv.html?highlight=make_lcmv#mne.beamformer.make_lcmv" target="_blank">make_lcmv</a>

.. |apply_lcmv_raw| raw:: html

   <a href="https://mne.tools/stable/generated/mne.beamformer.apply_lcmv_raw.html?highlight=apply_lcmv_raw#mne.beamformer.apply_lcmv_raw" target="_blank">apply_lcmv_raw</a>


.. code-block:: python
   :emphasize-lines: 56, 57, 58, 59

    def _compute_LCMV_inverse_solution(raw_filename, sbj_id, subjects_dir, fwd_filename, cov_fname, parc='aparc',
                                    all_src_space=False, ROIs_mean=True, is_fixed=False):
        """
        Compute the inverse solution on raw data by LCMV and return the average
        time series computed in the N_r regions of the source space defined by
        the specified cortical parcellation

        Inputs
            raw_filename : str
                filename of the raw data
            sbj_id : str
                subject name
            subjects_dir : str
                Freesurfer directory
            fwd_filename : str
                filename of the forward operator
            cov_filename : str
                filename of the noise covariance matrix
            parc: str
                the parcellation defining the ROIs atlas in the source space
            all_src_space: bool
                if True we compute the inverse for all points of the s0urce space
            ROIs_mean: bool
                if True we compute the mean of estimated time series on ROIs


        Outputs
            ts_file : str
                filename of the file where are saved the estimated time series
            labels_file : str
                filename of the file where are saved the ROIs of the parcellation
            label_names_file : str
                filename of the file where are saved the name of the ROIs of the
                parcellation
            label_coords_file : str
                filename of the file where are saved the coordinates of the
                centroid of the ROIs of the parcellation

        """
        print(('\n*** READ raw filename %s ***\n' % raw_filename))
        raw = read_raw_fif(raw_filename, preload=True)

        subj_path, basename, ext = split_f(raw_filename)

        print(('\n*** READ noise covariance %s ***\n' % cov_fname))
        noise_cov = mne.read_cov(cov_fname)

        print(('\n*** READ FWD SOL %s ***\n' % fwd_filename))
        forward = mne.read_forward_solution(fwd_filename)
        forward = mne.convert_forward_solution(forward, surf_ori=True)

        # compute data covariance matrix
        picks = pick_types(raw.info, meg=True, ref_meg=False, exclude='bads')
        data_cov = mne.compute_raw_covariance(raw, picks=picks)

        # compute LCMV filters
        filters = make_lcmv(raw.info, forward, data_cov, reg=0.05, noise_cov=noise_cov, pick_ori='normal', weight_norm='nai', depth=0.8)
        # apply spatial filter
        stc = apply_lcmv_raw(raw, filters, max_ori_out='signed')

        ts_file, label_ts, labels_file, label_names_file, label_coords_file = \
            _process_stc(stc, basename, sbj_id, subjects_dir, parc, forward, False, is_fixed, all_src_space=False, ROIs_mean=True)

        return ts_file, labels_file, label_names_file, label_coords_file

      
**Download** Json parameters file: :download:`params_LCMV_inverse.json <../../examples/params_LCMV_inverse.json>`

**Download** Python source code: :download:`plot_inverse_LCMV.py <../../examples/plot_inverse_LCMV.py>`



