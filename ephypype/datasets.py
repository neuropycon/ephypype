"""Functions to fetch online data."""

# Authors: Mainak Jas <mainakjas@gmail.com>
#
# License: BSD (3-clause)

import os
import zipfile
from mne.datasets.utils import _fetch_file


def fetch_omega_dataset(base_path):
    src_url = ('https://www.dropbox.com/sh/feqtjna1ymok445/'
               'AACStCwNgIlG3VcePkkTALgBa?dl=1')

    data_path = os.path.join(base_path, 'sample_BIDS_omega')
    target = os.path.join(base_path, 'sample_BIDS_omega.zip')

    if not os.path.exists(data_path):
        if not os.path.exists(target):
            _fetch_file(src_url, target)
        zf = zipfile.ZipFile(target, 'r')
        print('Extracting files. This may take a while ...')
        zf.extractall(path=data_path)
        os.remove(target)
    return os.path.abspath(data_path)


def fetch_ieeg_dataset(base_path):
    src_url = ('https://www.dropbox.com/s/njqtyk8j8bzdz8s/'
               'SubjectUCI29_data.mat?dl=1')

    data_path = os.path.join(base_path, 'ieeg')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    target = os.path.join(data_path, 'SubjectUCI29_data.mat')
    if not os.path.exists(target):
        _fetch_file(src_url, target)
        print('Downloading files ...')
    return os.path.abspath(data_path)


def fetch_erpcore_dataset(base_path):
    src_url = ('https://www.dropbox.com/sh/alcgilgobduusv0/'
               'AADoXFMCxRAwcMlLJ7zVS7q8a?dl=1')

    data_path = os.path.join(base_path, 'ERP_CORE')
    target = os.path.join(base_path, 'ERP_CORE.zip')

    if not os.path.exists(data_path):
        if not os.path.exists(target):
            _fetch_file(src_url, target)
        zf = zipfile.ZipFile(target, 'r')
        print('Extracting files. This may take a while ...')
        zf.extractall(path=data_path)
        os.remove(target)
    return os.path.abspath(data_path)
