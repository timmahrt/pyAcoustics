#!/usr/bin/env python
# encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''
from distutils.core import setup
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
      long_description=open('README.rst', 'r').read(),
#       install_requires=[], # No requirements! # requires 'from setuptools import setup'
      )
