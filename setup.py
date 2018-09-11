#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup configuration."""

import os
from setuptools import setup, find_packages
import ephypype

VERSION = None
with open(os.path.join('ephypype', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            VERSION = line.split('=')[1].strip().strip('\'')
            break
        
if VERSION is None:
    raise RuntimeError('Could not determine version')

if __name__ == "__main__":
    setup(
        name='ephypype',
        version=VERSION,
        packages=find_packages(),
        author=['David Meunier',
                'Annalisa Pascarella',
                'Dmitrii Altukhov'],
        description='Definition of functions used\
                     as Node for electrophy (EEG/MEG)\
                     pipelines within nipype framework',
        lisence='BSD 3',
        install_requires=['mne>=0.14',
                          'nipype',
                          'configparser',
                          'h5py']
    )
