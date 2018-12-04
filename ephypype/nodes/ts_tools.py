# -*- coding: utf-8 -*-
"""All nodes for import that are NOT specific to a ephy package."""
import numpy as np
import os

from nipype.interfaces.base import (BaseInterface, BaseInterfaceInputSpec,
                                    traits, TraitedSpec)


class SplitWindowsInputSpec(BaseInterfaceInputSpec):
    """Split window input spec."""

    ts_file = traits.File(
        exists=True, desc='nodes * time series in .npy format', mandatory=True)

    n_windows = traits.List(traits.Tuple, desc='List of start and stop points \
                            (tuple of two integers) of temporal windows',
                            mandatory=True)


class SplitWindowsOutputSpec(TraitedSpec):
    """Split window output spec."""

    win_ts_files = traits.List(traits.File(
        exists=True), desc="List of files with splitted timeseries by windows")


class SplitWindows(BaseInterface):
    """Split time series in several windows for all trials.

    Then save each ndarray as an independant numpy file .npy

    Parameters
    ----------
    ts_file:
        type = File, exists=True, desc='nodes * time series in .npy format',
        mandatory=True
    n_windows
        type = List(Tuple), desc='List of start and stop points (tuple of two
        integers)of temporal windows', mandatory = True

    Returns
    -------
    ts_file
        type = File, exists=True, desc="time series in .npy format"

    """

    input_spec = SplitWindowsInputSpec
    output_spec = SplitWindowsOutputSpec

    def _run_interface(self, runtime):

        print('in SplitWindows')

        np_ts = np.load(self.inputs.ts_file)

        print((np_ts.shape))

        self.win_ts_files = []

        print((self.inputs.n_windows))

        for i, n_win in enumerate(self.inputs.n_windows):

            print(i)
            print(n_win)

            if 0 <= n_win[0] and n_win[1] <= np_ts.shape[2]:

                # print "OK for : 0 <= {} and {} <= {}".format(n_win[0],
                # n_win[1],np_ts.shape[2])

                win_ts = []

                for trial_index in range(np_ts.shape[0]):

                    # print trial_index

                    # print np_ts[trial_index,:,n_win[0]:n_win[1]]

                    win_ts.append(np_ts[trial_index, :, n_win[0]:n_win[1]])

                win_ts = np.array(win_ts)

                # win_ts = np.array([np_ts[trial_index,:,n_win[0]:n_win[1]]]
                # for trial_index in range(np_ts.shape[0]))

                print((win_ts.shape))

                win_ts_file = os.path.abspath("win_ts_{}.npy".format(i))

                np.save(win_ts_file, win_ts)

                self.win_ts_files.append(win_ts_file)

            else:
                print(("Warning, should be : 0 <= {} and {} <= {}".format(
                    n_win[0], n_win[1], np_ts.shape[2])))
                0 / 0

        print(("Generated {} win files".format(len(self.win_ts_files))))

        return runtime

    def _list_outputs(self):

        outputs = self._outputs().get()

        outputs["win_ts_files"] = self.win_ts_files

        return outputs
