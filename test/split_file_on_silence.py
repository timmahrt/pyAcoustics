'''
Created on May 5, 2015

@author: tmahrt
'''

import os
from os.path import join


import praatio
from pyacoustics.signals import audio_scripts


def splitOnSilence(inputFN):

    silenceThreshold = audio_scripts.findQuietestSilence(inputFN, 1, 0.1)
    silenceList = audio_scripts.findSilences(inputFN, silenceThreshold)
    duration = audio_scripts.getSoundFileDuration(inputFN)
    tier = praatio.IntervalTier("silence", silenceList, minT=0, maxT=duration)
    
    tg = praatio.Textgrid()
    tg.addTier(tier)
    
    path = os.path.split(inputFN)[0]
    name = os.path.splitext(inputFN)[0]
    tg.save(join(path, name + ".TextGrid"))


if __name__ == "__main__":
    
    splitOnSilence("/Users/tmahrt/Desktop/ehp_force_align/subjects/1961.wav")
