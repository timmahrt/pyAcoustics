'''
Created on Jun 7, 2015

@author: tmahrt
'''

import struct
import wave
import math

from pyacoustics.signals import audio_scripts


class EndOfAudioData(Exception):
    pass


def getSoundFileDuration(fn):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    framerate = params[2]
    nframes = params[3]
    
    duration = float(nframes) / framerate
    return duration


def openAudioFile(fn):
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    sampwidth = params[1]
    framerate = params[2]
    
    return audiofile, sampwidth, framerate


def rms(audioFrameList):
    audioFrameList = [val ** 2 for val in audioFrameList]
    meanVal = sum(audioFrameList) / len(audioFrameList)
    return math.sqrt(meanVal)


def overlapCheck(interval, cmprInterval, percentThreshold=0):
    '''Checks whether two intervals overlap'''
    
    startTime, endTime = interval[0], interval[1]
    cmprStartTime, cmprEndTime = cmprInterval[0], cmprInterval[1]
    
    overlapTime = min(endTime, cmprEndTime) - max(startTime, cmprStartTime)
    overlapTime = max(0, overlapTime)
    overlapFlag = overlapTime > 0
    
    if percentThreshold > 0 and overlapFlag:
        totalTime = max(endTime, cmprEndTime) - min(startTime, cmprStartTime)
        percentOverlap = overlapTime / float(totalTime)
        
        overlapFlag = percentOverlap >= percentThreshold
    
    return overlapFlag


def getMinMaxAmplitude(wavFN, stepSize, entryList=None):
    
    audiofile = openAudioFile(wavFN)[0]
    
    # By default, find the min and max amplitude for the whole file
    if entryList is None:
        stop = audio_scripts.getSoundFileDuration(wavFN)
        entryList = [(0, stop), ]
    
    # Accumulate relevant energy values
    rmsList = []
    for entry in entryList:
        start, stop = entry[0], entry[1]
        currentTime = start
        while currentTime < stop:
            rmsList.append(rmsNextFrames(audiofile, stepSize))
            currentTime += stepSize
    
    # Return the min and max values
    minValue = min(rmsList)
    maxValue = max(rmsList)
    
    return minValue, maxValue


def rmsNextFrames(audiofile, stepSize, normMinVal=None, normMaxVal=None):
    
    params = audiofile.getparams()
    sampwidth, framerate = params[1], params[2]

    numFrames = int(framerate * stepSize)
    waveData = audiofile.readframes(numFrames)

    if len(waveData) == 0:
        raise EndOfAudioData()

    actualNumFrames = int(len(waveData) / float(sampwidth))
    audioFrameList = struct.unpack("<" + "h" * actualNumFrames, waveData)
    
    rmsEnergy = rms(audioFrameList)

    if normMinVal is not None and normMaxVal is not None:
        rmsEnergy = (rmsEnergy - normMinVal) / (normMaxVal - normMinVal)

    return rmsEnergy


def mergeAdjacentEntries(entryList):
    
    i = 0
    while i < len(entryList) - 1:
        
        if entryList[i][1] == entryList[i + 1][0]:
            startEntry = entryList.pop(i)
            nextEntry = entryList.pop(i)
            
            entryList.insert(i, (startEntry[0], nextEntry[1]))
        else:
            i += 1
            
    return entryList


def cropUnusedPortion(entry, start, stop):
    
    retEntryList = []
    
    if entry[0] < start:
        retEntryList.append((entry[0], start))
    
    if entry[1] > stop:
        retEntryList.append((stop, entry[1]))
    
    return retEntryList
