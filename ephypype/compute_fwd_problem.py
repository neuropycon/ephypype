"""Lead Field computation functions."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)
import mne
import glob
import os.path as op

from nipype.utils.filemanip import split_filename as split_f


def _create_bem_sol(subjects_dir, sbj_id):
    """Create bem solution."""
    import mne
    import os.path as op
    from mne.report import Report
    from mne.bem import make_watershed_bem
    report = Report()

    bem_dir = op.join(subjects_dir, sbj_id, 'bem')

    surf_name = 'inner_skull.surf'
    sbj_inner_skull_fname = op.join(bem_dir, sbj_id + '-' + surf_name)
    inner_skull_fname = op.join(bem_dir, surf_name)

    # check if bem-sol was created, if not creates the bem sol using MNE
    bem_fname = op.join(bem_dir, '{}-5120-bem-sol.fif'.format(sbj_id))
    model_fname = op.join(bem_dir, '{}-5120-bem.fif'.format(sbj_id))

    if not op.isfile(bem_fname):
        # chek if inner_skull surf exists, if not BEM computation is
        # performed by MNE python functions mne.bem.make_watershed_bem
        if not (op.isfile(sbj_inner_skull_fname) or
                op.isfile(inner_skull_fname)):
            print("{} ---> FILE NOT FOUND!!!---> BEM "
                  "computed".format(inner_skull_fname))
            make_watershed_bem(sbj_id, subjects_dir, overwrite=True)
        else:
            print(("\n*** inner skull {} surface "
                   "exists!!!\n".format(inner_skull_fname)))

        # Create a BEM model for a subject
        surfaces = mne.make_bem_model(sbj_id, ico=4, conductivity=[0.3],
                                      subjects_dir=subjects_dir)

        # Write BEM surfaces to a fiff file
        mne.write_bem_surfaces(model_fname, surfaces)

        # Create a BEM solution using the linear collocation approach
        bem = mne.make_bem_solution(surfaces)
        mne.write_bem_solution(bem_fname, bem)

        print(('\n*** BEM solution file {} written ***\n'.format(bem_fname)))

        # Add BEM figures to a Report
        report.add_bem_to_section(subject=sbj_id, subjects_dir=subjects_dir)
        report_filename = op.join(bem_dir, "BEM_report.html")
        print(('\n*** REPORT file {} written ***\n'.format(report_filename)))
        print(report_filename)
        report.save(report_filename, open_browser=False, overwrite=True)
    else:
        bem = bem_fname
        print(('\n*** BEM solution file {} exists!!! ***\n'.format(bem_fname)))

    return bem


def _create_src_space(subjects_dir, sbj_id, spacing):
    """Create a source space."""
    bem_dir = op.join(subjects_dir, sbj_id, 'bem')

    # check if source space exists, if not it creates using mne-python fun
    # we have to create the cortical surface source space even when aseg is
    # True
    src_fname = op.join(bem_dir, '%s-%s-src.fif' % (sbj_id, spacing))
    print('*** subject dir {}'.format(subjects_dir))
    if not op.isfile(src_fname):
        src = mne.setup_source_space(sbj_id, subjects_dir=subjects_dir,
                                     spacing=spacing.replace('-', ''),
                                     add_dist=False, n_jobs=1)

        mne.write_source_spaces(src_fname, src, overwrite=True)
        print(('\n*** source space file %s written ***\n' % src_fname))
    else:
        print(('\n*** source space file %s exists!!!\n' % src_fname))
        src = mne.read_source_spaces(src_fname)

    return src


def _create_mixed_source_space(subjects_dir, sbj_id, spacing, labels, src,
                               save_mixed_src_space):
    """Create a miwed source space."""

    bem_dir = op.join(subjects_dir, sbj_id, 'bem')

    src_aseg_fname = op.join(bem_dir, '%s-%s-aseg-src.fif' % (sbj_id, spacing))
    if not op.isfile(src_aseg_fname):

        aseg_fname = op.join(subjects_dir, sbj_id, 'mri/aseg.mgz')

        if spacing == 'oct-6':
            pos = 5.0
        elif spacing == 'oct-5':
            pos = 7.0
        elif spacing == 'ico-5':
            pos = 3.0

        model_fname = op.join(bem_dir, '%s-5120-bem.fif' % sbj_id)
        for l in labels:
            print(l)
            vol_label = mne.setup_volume_source_space(sbj_id, mri=aseg_fname,
                                                      pos=pos,
                                                      bem=model_fname,
                                                      volume_label=l,
                                                      subjects_dir=subjects_dir)  # noqa
            src += vol_label

        if save_mixed_src_space:
            mne.write_source_spaces(src_aseg_fname, src, overwrite=True)
            print("\n*** source space file {} written "
                  "***\n".format(src_aseg_fname))

        # Export source positions to nift file
        nii_fname = op.join(bem_dir, '%s-%s-aseg-src.nii' % (sbj_id, spacing))

        # Combine the source spaces
        src.export_volume(nii_fname, mri_resolution=True, overwrite=True)
    else:
        print("\n*** source space file {} "
              "exists!!!\n".format(src_aseg_fname))
        src = mne.read_source_spaces(src_aseg_fname)
        print(('src contains {} src spaces'.format(len(src))))
        for s in src[2:]:
            print(('sub structure {} \n'.format(s['seg_name'])))

    return src


def _is_trans(raw_fname, subject_id, trans_fname_template=None):
    """Check if coregistration file."""
    data_path, raw_fname, ext = split_f(raw_fname)

    if not trans_fname_template:
        raw_fname_4trans = raw_fname
        raw_fname_4trans = raw_fname_4trans.replace('_', '*')
        raw_fname_4trans = raw_fname_4trans.replace('-', '*')
        raw_fname_4trans = raw_fname_4trans.replace('filt', '*')
        raw_fname_4trans = raw_fname_4trans.replace('dsamp', '*')
        raw_fname_4trans = raw_fname_4trans.replace('ica', '*')
        raw_fname_4trans = raw_fname_4trans.replace('raw', '*')

        trans_fpath = op.join(data_path, '%s*trans.fif' % raw_fname_4trans)
    else:
        trans_fpath = trans_fname_template.format(sbj=subject_id)

    trans_files = glob.glob(trans_fpath)
    assert len(trans_files) == 1, "Error, should be only one trans file"

    trans_fname = trans_files[0]
    print(('\n*** coregistration file %s found!!!\n' % trans_fname))

    if not op.isfile(trans_fname):
        raise RuntimeError('*** coregistration file %s NOT found!!!'
                           % trans_fname)

    return trans_fname


def _get_fwd_filename(raw_fpath, aseg, spacing):

    data_path, raw_fname, ext = split_f(raw_fpath)
    fwd_filename = raw_fname + '-' + spacing
    if aseg:
        fwd_filename += '-aseg'

    fwd_filename = op.join(data_path, fwd_filename + '-fwd.fif')

    print(('\n *** fwd_filename {} ***\n'.format(fwd_filename)))
    return fwd_filename


def _compute_fwd_sol(raw_fname, trans_fname, src, bem, fwd_filename):
    """Compute leadfield matrix by BEM."""
    mindist = 5.  # ignore sources <= 0mm from inner skull
    fwd = mne.make_forward_solution(raw_fname, trans_fname, src, bem,
                                    mindist=mindist, meg=True, eeg=False,
                                    n_jobs=2)

    mne.write_forward_solution(fwd_filename, fwd, overwrite=True)
    print(('\n*** FWD file {} written!!!\n'.format(fwd_filename)))
