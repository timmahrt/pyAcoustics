'''
Created on Sep 6, 2014

@author: tmahrt
'''

import os
from os.path import join
import math

from pyacoustics.signals import audio_scripts
from pyacoustics.utilities import sequences

BEEP = "beep"
SILENCE = "silence"
SPEECH = "speech"


def _homogenizeList(dataList, toneFrequency):
    '''
    Discritizes pitch values into one of three categories
    '''
    
    minVal = min(dataList)
    
    retDataList = []
    for val in dataList:
        if val == toneFrequency:
            val = BEEP
        elif val == minVal:
            val = SILENCE
        else:
            val = SPEECH
        retDataList.append(val)
        
    return retDataList


def splitFileOnTone(pitchList, timeStep, toneFrequency,
                    eventDurationThreshold):
    '''
    Splits files by pure tones
    '''
    toneFrequency = int(round(toneFrequency, -1))
    
    roundedPitchList = [int(round(val, -1)) for val in pitchList]
    codedPitchList = _homogenizeList(roundedPitchList, toneFrequency)
    
    compressedList = sequences.compressList(codedPitchList)
    timeDict = sequences.compressedListTransform(compressedList,
                                                 1.0/timeStep,
                                                 eventDurationThreshold)
    
    # Fill in with empty lists if it didn't appear in the dataset
    # (eg no beeps were detected or no speech occurred)
    for key in [BEEP, SPEECH, SILENCE]:
        if key not in timeDict:
            timeDict[key] = []

    return timeDict
    

def extractSubwavs(timeDict, path, fn, outputPath):
    '''
    Extracts segments between tones marked in the output of splitFileOnTone()
    '''
    name = os.path.splitext(fn)[0]
    
    duration = audio_scripts.getSoundFileDuration(join(path, fn))
    beepEntryList = timeDict[BEEP]
    segmentEntryList = sequences.invertIntervalList(beepEntryList, 0, duration)
    
    if len(segmentEntryList) > 0:
        numZeroes = int(math.floor(math.log10(len(segmentEntryList)))) + 1
    else:
        numZeroes = 1
        
    strFmt = "%%s_%%0%dd.wav" % numZeroes  # e.g. '%s_%02d.wav'

    for i, entry in enumerate(segmentEntryList):
        start, stop = entry[:2]
        
        audio_scripts.extractSubwav(join(path, fn),
                                    join(outputPath, strFmt % (name, i)),
                                    startT=float(start), endT=float(stop),
                                    singleChannelFlag=True)
