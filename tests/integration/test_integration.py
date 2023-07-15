#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Nov 21, 2021

@author: tmahrt

Runs integration tests

The examples were all written as scripts.  They weren't meant to be
imported or run from other code.  So here, the integration test is just
importing the scripts, which causes them to execute.  If the code completes
with no errors, then the code is at least able to complete.

Testing whether or not the code actually did what it is supposed to is
another issue and will require some refactoring.
"""

import unittest
import os
import sys
from pathlib import Path

_root = os.path.join(Path(__file__).parents[2], "examples")
sys.path.append(_root)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_estimate_speech_rate(self):
        """Running 'add_tiers.py'"""
        import estimate_speech_rate

    def test_frequency(self):
        """Running 'anonymize_recording'"""
        import frequency

    def test_split_audio_on_silence(self):
        """Running 'calculate_duration.py'"""
        import split_audio_on_silence

    def test_split_audio_on_tone(self):
        """Running 'correct_misaligned_tiers.py'"""
        import split_audio_on_tone

    def setUp(self):
        unittest.TestCase.setUp(self)

        root = os.path.join(_root, "files")
        self.oldRoot = os.getcwd()
        os.chdir(_root)
        self.startingList = os.listdir(root)
        self.startingDir = os.getcwd()

    def tearDown(self):
        """Remove any files generated during the test"""
        # unittest.TestCase.tearDown(self)

        root = os.path.join(".", "files")
        endingList = os.listdir(root)
        endingDir = os.getcwd()
        rmList = [fn for fn in endingList if fn not in self.startingList]

        if self.oldRoot == root:
            for fn in rmList:
                fnFullPath = os.path.join(root, fn)
                if os.path.isdir(fnFullPath):
                    os.rmdir(fnFullPath)
                else:
                    os.remove(fnFullPath)

        os.chdir(self.oldRoot)


if __name__ == "__main__":
    unittest.main()
