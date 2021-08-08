#!/usr/bin/env python
# encoding: utf-8
"""
Created on Oct 15, 2014

@author: tmahrt
"""
from setuptools import setup
import io

setup(
    name="pyacoustics",
    version="1.0.7",
    author="Tim Mahrt",
    author_email="timmahrt@gmail.com",
    url="https://github.com/timmahrt/pyAcoustics",
    package_dir={"pyacoustics": "pyacoustics"},
    packages=[
        "pyacoustics",
        "pyacoustics.intensity_and_pitch",
        "pyacoustics.signals",
        "pyacoustics.speech_detection",
        "pyacoustics.speech_rate",
        "pyacoustics.text",
        "pyacoustics.textgrids",
        "pyacoustics.utilities",
    ],
    package_data={
        "pyacoustics": [
            "matlabScripts/detect_syllable_nuclei.m",
        ]
    },
    license="LICENSE",
    install_requires=["praatio ~= 4.1"],
    description="A collection of python scripts for extracting and analyzing acoustics from audio files.",
    long_description=io.open("README.rst", "r", encoding="utf-8").read(),
)
