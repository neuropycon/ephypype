#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup configuration."""

from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name='ephypype',
        # version=VERSION,
        version='0.1.dev0',
        packages=find_packages(),
        author=['David Meunier',
                'Annalisa Pascarella',
                'Dmitrii Altukhov'],
        description='Definition of functions used\
                     as Node for electrophy (EEG/MEG)\
                     pipelines within nipype framework',
        lisence='BSD 3',
        install_requires=['mne>=0.16',
                          'nipype',
                          'configparser',
                          'h5py']
    )
