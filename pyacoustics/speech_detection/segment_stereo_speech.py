'''
Created on Nov 4, 2014

@author: tmahrt
'''

import wave
import struct
import math

import praatio

from pyacoustics.signals import audio_scripts


class EndOfAudioData(Exception):
    pass


def _openAudioFile(fn):
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    nchannels, sampwidth, framerate, nframes, comptype, compname = params
    
    return audiofile, sampwidth, framerate


def _cropUnusedPortion(entry, start, stop):
    
    retEntryList = []
    
    if entry[0] < start:
        retEntryList.append( (entry[0], start) )
    
    if entry[1] > stop:
        retEntryList.append( (stop, entry[1]) )
    
    return retEntryList


def _mergeAdjacentEntries(entryList):
    
    i = 0
    while i < len(entryList) - 1:
        
        if entryList[i][1] == entryList[i+1][0]:
            startEntry = entryList.pop(i)
            nextEntry = entryList.pop(i)
            
            entryList.insert(i, (startEntry[0], nextEntry[1]))
        else:
            i += 1
            
    return entryList
    
    
def _rmsNextFrames(audiofile, stepSize, normMinVal=None, normMaxVal=None):
    
    params = audiofile.getparams()
    sampwidth, framerate = params[1], params[2]

    numFrames = int(framerate * stepSize)
    waveData = audiofile.readframes(numFrames)

    if len(waveData) == 0:
        raise EndOfAudioData()

    actualNumFrames = int(len(waveData) / float(sampwidth))
    audioFrameList = struct.unpack("<"+"h"*actualNumFrames, waveData)        
    
    rmsEnergy = _rms(audioFrameList)    

    if normMinVal != None and normMaxVal != None:
        rmsEnergy = (rmsEnergy - normMinVal) / (normMaxVal - normMinVal)

    return rmsEnergy


def _rms(audioFrameList):
    audioFrameList = [val**2 for val in audioFrameList]
    meanVal = sum(audioFrameList) / len(audioFrameList)
    return math.sqrt(meanVal)


def _overlapCheck(interval, cmprInterval, percentThreshold=0):
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


def findNextSpeaker(leftSamples, rightSamples, samplingFreq,
                    startTime, analyzeStop, stepSize,
                    numSteps, findLeft=True):
    '''
    
    '''
    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    while currentSequenceNum < numSteps:

        # Stop analyzing once we've reached the end of this interval
        currentTime = startTime + i * stepSize
        nextTime = startTime + ((i+1) * stepSize)

        if nextTime > analyzeStop:
            raise EndOfAudioData()

        leftRMSEnergy = _rms(leftSamples[int(currentTime*samplingFreq):
                                         int(nextTime*samplingFreq)])
        rightRMSEnergy = _rms(rightSamples[int(currentTime*samplingFreq):
                                           int(nextTime*samplingFreq)])
        
        if ((findLeft == True and leftRMSEnergy >= rightRMSEnergy) or
           (findLeft == False and leftRMSEnergy <= rightRMSEnergy)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime 


def assignAudioEventsForEntries(leftSamples, rightSamples, samplingFreq, 
                                leftEntry, rightEntry, stepSize, 
                                speakerNumSteps):
    '''
    Start up and tear down function for assignAudioEvents()
    '''
    
    # Find the overlap interval and preserve the non-overlapped portions
    start = max(leftEntry[0], rightEntry[0])
    stop = min(leftEntry[1], rightEntry[1])
    
    leftEntryList = _cropUnusedPortion(leftEntry, start, stop)
    rightEntryList = _cropUnusedPortion(rightEntry, start, stop)
    
    # Determine who is speaking in overlapped portions
    tmpEntries = assignAudioEvents(leftSamples, rightSamples, samplingFreq,
                                   start, stop, stepSize, speakerNumSteps)
    
    leftEntryList.extend(tmpEntries[0])
    rightEntryList.extend(tmpEntries[1])
    
    # Merge adjacent regions sharing a boundary, if any
    leftEntryList.sort()
    rightEntryList.sort()
    
    leftEntryList = _mergeAdjacentEntries(leftEntryList)
    rightEntryList = _mergeAdjacentEntries(rightEntryList)
    
    return leftEntryList, rightEntryList


def assignAudioEvents(leftSamples, rightSamples, samplingFreq, startTime, 
                      analyzeStop, stepSize, speakerNumSteps):

    findLeft = True    
    leftEntryList = []
    rightEntryList = []
    try:
        while True:
            endTime = findNextSpeaker(leftSamples, rightSamples, 
                                      samplingFreq, startTime, 
                                      analyzeStop, stepSize, 
                                      speakerNumSteps, findLeft)
            
            if endTime > analyzeStop:
                endTime = analyzeStop
            
            if startTime != endTime:
                entry = (startTime, endTime)
                if findLeft:
                    leftEntryList.append(entry)
                else:
                    rightEntryList.append(entry)
            
            print startTime, endTime, analyzeStop
            startTime = endTime
            findLeft = not findLeft
        
    except EndOfAudioData: # Stop processing
    
        if analyzeStop - startTime > stepSize * speakerNumSteps:
            finalEntry = (startTime, analyzeStop)
            if findLeft:
                leftEntryList.append(finalEntry)
            else:
                rightEntryList.append(finalEntry)
    
    return leftEntryList, rightEntryList


def getMinMaxAmplitude(wavFN, stepSize, entryList=None):
    
    audiofile = _openAudioFile(wavFN)[0]
    
    # By default, find the min and max amplitude for the whole file
    if entryList == None:
        stop = audio_scripts.getSoundFileDuration(wavFN)
        entryList = [(0, stop),]
    
    # Accumulate relevant energy values
    rmsList = []
    for entry in entryList:
        start, stop = entry[0], entry[1]
        currentTime = start
        while currentTime < stop:
            rmsList.append(_rmsNextFrames(audiofile, stepSize))
            currentTime += stepSize
    
    # Return the min and max values
    minValue = min(rmsList)
    maxValue = max(rmsList)
    
    return minValue, maxValue


def autosegmentStereoAudio(leftSamples, rightSamples, samplingFreq,
                           leftEntryList, rightEntryList,
                           stepSize, speakerNumSteps):

    overlapThreshold = 0    
    overlapCheck = (lambda entry, entryList: 
                    [not _overlapCheck(entry, cmprEntry, overlapThreshold) 
                     for cmprEntry in entryList]
                    )
    
    # First add all of the entries with no overlap
    newLeftEntryList = []
    for leftEntry in leftEntryList:
        
        if all(overlapCheck(leftEntry, rightEntryList)):
            newLeftEntryList.append(leftEntry)
            
    newRightEntryList = []
    for rightEntry in rightEntryList:
        
        if all(overlapCheck(rightEntry, leftEntryList)):
            newRightEntryList.append(rightEntry)
        
    # For all entries with overlap, split them by speaker
    # Utilizing the left channel as a base, this chunks through all overlapping
    # in a single pass of the left channel, until there are no more overlapping
    # segments between the right and left channels.
    i = 0
    while i < len(leftEntryList):
        
        # Check if there are any segments in the right channel that overlap 
        # with the current segment in the left channel.  If not, move to 
        # the next segment.
        leftEntry = leftEntryList[i]
        overlapCheckList = overlapCheck(leftEntry, rightEntryList)
        if all(overlapCheckList):
            i += 1
            continue
        
        # Otherwise, resolve the first segment in the right channel that
        # overlaps with the current segment
        leftEntry = leftEntryList.pop(i)
        
        j = overlapCheckList.index(False) # Find the first overlap
        rightEntry = rightEntryList.pop(j)
        
        entryTuple = assignAudioEventsForEntries(leftSamples, rightSamples, 
                                                 samplingFreq,
                                                 leftEntry, rightEntry, stepSize, 
                                                 speakerNumSteps)
        tmpLeftEntryList, tmpRightEntryList = entryTuple
        
        leftEntryList[i:i] = tmpLeftEntryList
        rightEntryList[j:j] = tmpRightEntryList

    # Combine the original non-overlapping segments with the adjusted segments
    newLeftEntryList.extend(leftEntryList)
    newRightEntryList.extend(rightEntryList)
    
    newLeftEntryList.sort()
    newRightEntryList.sort()
    
    newLeftEntryList = [entry for entry in newLeftEntryList 
                        if (entry[1]-entry[0] > stepSize*speakerNumSteps)]
    newRightEntryList = [entry for entry in newRightEntryList 
                         if (entry[1]-entry[0] > stepSize*speakerNumSteps)]
    
    return newLeftEntryList, newRightEntryList
    




