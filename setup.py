#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup configuration."""

import os
from setuptools import setup, find_packages

required_packages=[
    "nipype", "networkx>=2.0", "numpy", "mne", "pybids", "h5py","scikit-learn", "matplotlib", "mne-bids"]

VERSION = None
with open(os.path.join('ephypype', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            VERSION = line.split('=')[1].strip().strip('\'')
            break

if VERSION is None:
    raise RuntimeError('Could not determine version')

descr = """Python package providing pipelines for electrophysiological (EEG/MEG) data within nipype framework."""

DISTNAME = 'ephypype'
DESCRIPTION = descr
MAINTAINER = 'Annalisa Pascarella'
MAINTAINER_EMAIL = 'a.pascarella@iac.cnr.it'
URL = 'https://neuropycon.github.io/ephypype/'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/neuropycon/ephypype'


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        version=VERSION,
        packages=find_packages(),
        author=['David Meunier',
                'Annalisa Pascarella',
                'Dmitrii Altukhov'],
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        download_url=DOWNLOAD_URL,
        long_description=open('README.rst').read(),
        long_description_content_type='text/markdown',
        entry_points='''
            [console_scripts]
            neuropycon=ephypype.commands.neuropycon:cli
            ''',
        install_requires= required_packages
    )
