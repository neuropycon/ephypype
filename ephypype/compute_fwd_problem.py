"""
Lead Field computation functions
"""
# Author: Annalisa Pascarella <a.pascarella@iac.cnr.it>


def create_bem_sol(sbj_dir, sbj_id):
    import os.path as op
    import mne

    from mne.bem import make_watershed_bem
    from mne.report import Report

    report = Report()

    bem_dir = op.join(sbj_dir, sbj_id, 'bem')

    surf_name = 'inner_skull.surf'
    sbj_inner_skull_fname = op.join(bem_dir, sbj_id + '-' + surf_name)
    inner_skull_fname = op.join(bem_dir, surf_name)

    # check if bem-sol was created, if not creates the bem sol using C MNE
    bem_fname = op.join(bem_dir, '%s-5120-bem-sol.fif' % sbj_id)
    model_fname = op.join(bem_dir, '%s-5120-bem.fif' % sbj_id)

    if not op.isfile(bem_fname):
        # chek if inner_skull surf exists, if not BEM computation is
        # performed by MNE python functions mne.bem.make_watershed_bem
        if not (op.isfile(sbj_inner_skull_fname) or
                op.isfile(inner_skull_fname)):
            print((inner_skull_fname + '---> FILE NOT FOUND!!!---> BEM computed'))
            make_watershed_bem(sbj_id, sbj_dir, overwrite=True)
        else:
            print(('\n*** inner skull %s surface exists!!!\n' % inner_skull_fname))

        # Create a BEM model for a subject
        surfaces = mne.make_bem_model(sbj_id, ico=4, conductivity=[0.3],
                                      subjects_dir=sbj_dir)

        # Write BEM surfaces to a fiff file
        mne.write_bem_surfaces(model_fname, surfaces)

        # Create a BEM solution using the linear collocation approach
        bem = mne.make_bem_solution(surfaces)
        mne.write_bem_solution(bem_fname, bem)

        print(('\n*** BEM solution file %s written ***\n' % bem_fname))

        # add BEM figures to a Report
        report.add_bem_to_section(subject=sbj_id, subjects_dir=sbj_dir)
        report_filename = op.join(bem_dir, "BEM_report.html")
        print(('\n*** REPORT file %s written ***\n' % report_filename))
        print(report_filename)
        report.save(report_filename, open_browser=False, overwrite=True)
    else:
        bem = bem_fname
        print(('\n*** BEM solution file %s exists!!! ***\n' % bem_fname))

    return bem


def create_src_space(sbj_dir, sbj_id, spacing):
    import os.path as op
    import mne

    bem_dir = op.join(sbj_dir, sbj_id, 'bem')

    # check if source space exists, if not it creates using mne-python fun
    # we have to create the cortical surface source space even when aseg is
    # True
    src_fname = op.join(bem_dir, '%s-%s-src.fif' % (sbj_id, spacing))
    if not op.isfile(src_fname):
        src = mne.setup_source_space(sbj_id, subjects_dir=sbj_dir,
                                     spacing=spacing.replace('-', ''),
                                     add_dist=False,
                                     n_jobs=2)

        mne.write_source_spaces(src_fname, src, overwrite=True)
        print(('\n*** source space file %s written ***\n' % src_fname))
    else:
        print(('\n*** source space file %s exists!!!\n' % src_fname))
        src = mne.read_source_spaces(src_fname)

    return src


def create_mixed_source_space(sbj_dir, sbj_id, spacing, labels, src,
                              save_mixed_src_space):
    import os.path as op
    import mne

    bem_dir = op.join(sbj_dir, sbj_id, 'bem')

    src_aseg_fname = op.join(bem_dir, '%s-%s-aseg-src.fif' % (sbj_id, spacing))
    if not op.isfile(src_aseg_fname):

        aseg_fname = op.join(sbj_dir, sbj_id, 'mri/aseg.mgz')

        if spacing == 'oct-6':
            pos = 5.0
        elif spacing == 'ico-5':
            pos = 3.0

        model_fname = op.join(bem_dir, '%s-5120-bem.fif' % sbj_id)
        for l in labels:
            print(l)
            vol_label = mne.setup_volume_source_space(sbj_id, mri=aseg_fname,
                                                      pos=pos,
                                                      bem=model_fname,
                                                      volume_label=l,
                                                      subjects_dir=sbj_dir)
            src += vol_label

        if save_mixed_src_space:
            mne.write_source_spaces(src_aseg_fname, src, overwrite=True)
            print(('\n*** source space file {} written ***\n'.format(src_aseg_fname)))

        # Export source positions to nift file
        nii_fname = op.join(bem_dir, '%s-%s-aseg-src.nii' % (sbj_id, spacing))

        # Combine the source spaces
        src.export_volume(nii_fname, mri_resolution=True)
    else:
        print(('\n*** source space file {} exists!!!\n'.format(src_aseg_fname)))
        src = mne.read_source_spaces(src_aseg_fname)
        print(('src contains {} src spaces'.format(len(src))))
        for s in src[2:]:
            print(('sub structure {} \n'.format(s['seg_name'])))

    return src


def is_trans(raw_fname):
    import glob
    import os.path as op

    from nipype.utils.filemanip import split_filename as split_f

    data_path, raw_fname, ext = split_f(raw_fname)

    # check if the co-registration file was created
    # if not raise an runtime error
#    i_ica = raw_fname.find('ica')
#    if i_ica != -1:
#        raw_fname = raw_fname[:i_ica]

    raw_fname_4trans = raw_fname
    raw_fname_4trans = raw_fname_4trans.replace('_', '*')
    raw_fname_4trans = raw_fname_4trans.replace('-', '*')
    raw_fname_4trans = raw_fname_4trans.replace('filt', '*')
    raw_fname_4trans = raw_fname_4trans.replace('dsamp', '*')
    raw_fname_4trans = raw_fname_4trans.replace('ica', '*')

    trans_fname = op.join(data_path, '%s*trans.fif' % raw_fname_4trans)
    for trans_fname in glob.glob(trans_fname):
        print(('\n*** coregistration file %s found!!!\n' % trans_fname))

    if not op.isfile(trans_fname):
        raise RuntimeError('*** coregistration file %s NOT found!!!'
                           % trans_fname)

    return trans_fname


def compute_fwd_sol(raw_info, trans_fname, src, bem, fwd_filename):
    """
    Compute leadfield matrix by BEM
    """
    import mne

    fwd = mne.make_forward_solution(raw_info, trans_fname, src, bem,
                                    mindist=5.0,  # ignore sources <= 0mm from inner skull
                                    meg=True, eeg=False,
                                    n_jobs=2)

    mne.write_forward_solution(fwd_filename, fwd, overwrite=True)
    print(('\n*** FWD file %s written!!!\n' % fwd_filename))
