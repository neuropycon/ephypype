"""LF computation Interface."""

# Authors: Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

import os.path as op

from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec
from nipype.interfaces.base import traits, File, TraitedSpec

from ...compute_fwd_problem import _create_mixed_source_space
from ...compute_fwd_problem import _create_bem_sol, _create_src_space
from ...compute_fwd_problem import _compute_fwd_sol
from ...compute_fwd_problem import _get_fwd_filename


class LFComputationConnInputSpec(BaseInterfaceInputSpec):
    """Input specification for LFComputation."""

    sbj_id = traits.String(desc='subject id', mandatory=True)
    subjects_dir = traits.String(exists=True, desc='Freesurfer main directory',
                                 mandatory=True)
    raw_fname = traits.String(desc='raw file name', mandatory=True)
    trans_file = traits.String(desc='trans file name', mandatory=False)
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
    """Output specification for LFComputation."""

    fwd_filename = File(exists=False, desc='LF matrix')


class LFComputation(BaseInterface):
    """Compute the Lead Field matrix using MNE Python functions.

    Inputs
    ------
    sbj_id : str
        subject name
    subjects_dir : str
        Freesurfer directory
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

    def _run_interface(self, runtime):

        sbj_id = self.inputs.sbj_id
        subjects_dir = self.inputs.subjects_dir
        raw_fname = self.inputs.raw_fname
        # trans_fname = self.inputs.trans_fname
        trans_file = self.inputs.trans_file
        aseg = self.inputs.aseg
        spacing = self.inputs.spacing
        aseg_labels = self.inputs.aseg_labels
        save_mixed_src_space = self.inputs.save_mixed_src_space

        self.fwd_filename = _get_fwd_filename(raw_fname, aseg,
                                              spacing)

        # check if we have just created the fwd matrix
        if not op.isfile(self.fwd_filename):
            print('\n*** Computing FWD matrix {} ***\n'.format(
                  self.fwd_filename))
            bem = _create_bem_sol(subjects_dir, sbj_id)  # bem solution

            src = _create_src_space(subjects_dir, sbj_id, spacing)  # src space

            if aseg:
                src = _create_mixed_source_space(subjects_dir, sbj_id, spacing,
                                                 aseg_labels, src,
                                                 save_mixed_src_space)

            n = sum(src[i]['nuse'] for i in range(len(src)))
            print('src space contains {} spaces and {} vertices'.format(
                len(src), n))

            _compute_fwd_sol(raw_fname, trans_file, src, bem,
                             self.fwd_filename)
        else:
            print(('\n*** FWD file {} exists!!!\n'.format(self.fwd_filename)))

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()
        outputs['fwd_filename'] = self.fwd_filename

        return outputs
