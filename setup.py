#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='ephypype',
    version='0.0.2',
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
                      'configparser']
)
