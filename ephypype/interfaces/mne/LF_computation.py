"""LF computation Interface."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import os.path as op

from nipype.utils.filemanip import split_filename as split_f

from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec
from nipype.interfaces.base import traits, File, TraitedSpec

from ...compute_fwd_problem import _create_mixed_source_space
from ...compute_fwd_problem import _create_bem_sol, _create_src_space
from ...compute_fwd_problem import _is_trans, _compute_fwd_sol


class LFComputationConnInputSpec(BaseInterfaceInputSpec):
    """LF computation conn input spec."""

    sbj_id = traits.String(desc='subject id', mandatory=True)
    sbj_dir = traits.String(exists=True, desc='Freesurfer main directory',
                            mandatory=True)
    raw_info = traits.Any(desc='raw info', mandatory=True)
    raw_fname = traits.String(desc='raw file name', mandatory=True)
    spacing = traits.String(desc='spacing to use to setup a source space',
                            mandatory=False)
    aseg = traits.Bool(desc='if true sub structures will be considered',
                       mandatory=False)
    aseg_labels = traits.List(desc='list of substructures in the src space',
                              mandatory=False)
    save_mixed_src_space = traits.Bool(False, desc='if true save src space',
                                       usedefault=True,
                                       mandatory=False)


class LFComputationConnOutputSpec(TraitedSpec):
    """LF computation conn output spec."""

    fwd_filename = File(exists=False, desc='LF matrix')


class LFComputation(BaseInterface):
    """Compute the Lead Field matrix using MNE Python functions.

    Inputs
    ------
    sbj_id : str
        subject name
    sbj_dir : str
        Freesurfer directory
    raw_info : dict
        information dictionary of the raw data
    raw_filename : str
        filename of the raw data
    spacing : str (default 'ico-5')
        spacing to use to setup a source space
    aseg: bool (defualt False)
        if True a mixed source space will be created and the sub cortical
        regions defined in aseg_labels will be added to the source space
    aseg_labels: list (default [])
        list of substructures we want to include in the mixed source space
    save_mixed_src_space: bool (default False)
        if True save the mixed src space

    Outputs
    -------
       fwd_filename : str
           Filename of the Lead Field matrix
    """

    input_spec = LFComputationConnInputSpec
    output_spec = LFComputationConnOutputSpec

    def _get_fwd_filename(self, raw_info, aseg, spacing):

        data_path, raw_fname, ext = split_f(raw_info)
        fwd_filename = '%s-%s' % (raw_fname, spacing)
        if aseg:
            fwd_filename += '-aseg'

        fwd_filename = op.join(data_path, fwd_filename + '-fwd.fif')

        print(('\n *** fwd_filename %s ***\n' % fwd_filename))
        return fwd_filename

    def _run_interface(self, runtime):

        sbj_id = self.inputs.sbj_id
        sbj_dir = self.inputs.sbj_dir
        raw_info = self.inputs.raw_info
        raw_fname = self.inputs.raw_fname
        aseg = self.inputs.aseg
        spacing = self.inputs.spacing
        aseg_labels = self.inputs.aseg_labels
        save_mixed_src_space = self.inputs.save_mixed_src_space

        self.fwd_filename = self._get_fwd_filename(raw_fname, aseg,
                                                   spacing)

        # check if we have just created the fwd matrix
        if not op.isfile(self.fwd_filename):
            bem = _create_bem_sol(sbj_dir, sbj_id)  # bem solution

            src = _create_src_space(sbj_dir, sbj_id, spacing)  # src space

            if aseg:
                src = _create_mixed_source_space(sbj_dir, sbj_id, spacing,
                                                 aseg_labels, src,
                                                 save_mixed_src_space)

            n = sum(src[i]['nuse'] for i in range(len(src)))
            print(('il src space contiene %d spaces e %d vertici'
                   % (len(src), n)))

            trans_fname = _is_trans(raw_fname)

            # TODO: ha senso una funzione con un solo cmd?
            _compute_fwd_sol(raw_info, trans_fname, src, bem,
                             self.fwd_filename)
        else:
            print(('\n*** FWD file %s exists!!!\n' % self.fwd_filename))

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['fwd_filename'] = self.fwd_filename

        return outputs
