#!/usr/bin/env python
# encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''
from distutils.core import setup
import codecs
setup(name='pyacoustics',
      version='1.0.0',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      package_dir={'pyacoustics':'pyacoustics'},
      packages=[
      			'pyacoustics',
      			'pyacoustics.intensity_and_pitch',
                'pyacoustics.signals',
                'pyacoustics.speech_detection',
                'pyacoustics.speech_rate',
                'pyacoustics.text',
                'pyacoustics.textgrids',
                'pyacoustics.utilities',
                ],
      license='LICENSE',
      description="A collection of python scripts for extracting and analyzing acoustics from audio files.",
      long_description=codecs.open('README.rst', 'r', encoding="utf-8").read(),
#       install_requires=[], # No requirements! # requires 'from setuptools import setup'
      )
