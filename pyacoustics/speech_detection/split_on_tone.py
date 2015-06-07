'''
Created on Sep 6, 2014

@author: tmahrt
'''

import os
from os.path import join
import math

import praatio

from pyacoustics.signals import audio_scripts
from pyacoustics.utilities import sequences
from pyacoustics.utilities import utils


def _homogenizeList(dataList):
    '''
    Discritizes pitch values into one of three categories
    '''
    
    minVal = min(dataList)
    
    retDataList = []
    for val in dataList:
        if val > 300:
            val = 'beep'
        elif val == minVal:
            val = 'silence'
        else:
            val = 'text'
        retDataList.append(val)
        
    return retDataList


def splitFileOnTone(path, fn, pitchList, pitchSampleFreq, createSubwavs=False,
                    eventDurationThreshold=0.2):
    '''
    Finds pure
    '''
    fileDuration = audio_scripts.getSoundFileDuration(join(path, fn))
    
    roundedPitchList = [round(val, -1) for val in pitchList]
    open(join(path, "rounded_pitch_list.txt"),
         "w").write("\n".join([str(val) for val in roundedPitchList]))
    roundedPitchList = _homogenizeList(roundedPitchList)
    
    compressedList = sequences.compressList(roundedPitchList)
    timeDict = sequences.compressedListTransform(compressedList,
                                                 pitchSampleFreq,
                                                 eventDurationThreshold)
    
    for blah in compressedList:
        print blah
    
    tg = praatio.Textgrid()
    for label, entryList in timeDict.items():
        
        entryList.sort()
        
        tier = praatio.IntervalTier(label, entryList, 0, fileDuration)
        tg.addTier(tier)
    
    tgFN = os.path.splitext(fn)[0] + ".TextGrid"
    tg.save(join(path, tgFN))
    
    if createSubwavs:
        extractSubwavs(path, fn, tgFN)
    

def extractSubwavs(path, fn, tgFN):
    '''
    Extracts segments marked in the output of splitFileOnTone()
    '''

    outputPath = join(path, "extractedWavs")
    utils.makeDir(outputPath)

    tg = praatio.openTextGrid(join(path, tgFN))
    tier = tg.tierDict["beep"]
    
    name = os.path.splitext(fn)[0]
    entryList = [entry for entry in praatio.fillInBlanks(tier.entryList, "")
                 if entry[2] == ""]
    
    numZeroes = int(math.floor(math.log10(len(entryList)))) + 1
    strFmt = "%%s_%%0%dd.wav" % numZeroes  # e.g. '%s_%02d.wav'

    for i, entry in enumerate(entryList):
        start, stop = entry[:2]
        
        audio_scripts.extractSubwav(join(path, fn),
                                    join(outputPath, strFmt % (name, i)),
                                    startT=float(start), endT=float(stop),
                                    singleChannelFlag=True)
