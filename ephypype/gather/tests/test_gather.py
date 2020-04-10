"""Test gather."""

from ephypype.gather.gather_results import get_results


def test_get_results():

    pipeline_names = ['connectivity', 'power', 'inverse', 'ica', 'tfr_morlet']

    for name in pipeline_names:
        res = get_results('',  '', name)

        assert res
