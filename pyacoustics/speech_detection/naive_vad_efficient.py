
import os
from os.path import join

import math
import struct
import wave
import audioop

import praatio


class EndOfAudioData(Exception):
    pass


def getSoundFileDuration(fn):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    nchannels, sampwidth, framerate, nframes, comptype, compname = params
    
    duration = float(nframes) / framerate
    return duration


def _openAudioFile(fn):
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    nchannels, sampwidth, framerate, nframes, comptype, compname = params
    
    return audiofile, sampwidth, framerate


def _rms(audioFrameList):
    audioFrameList = [val**2 for val in audioFrameList]
    meanVal = sum(audioFrameList) / len(audioFrameList)
    return math.sqrt(meanVal)


def findNextEvent(fn, startTime, silenceThreshold, stepSize,
                  numSteps, findSilence=True):
    '''
    
    if findSilence=False then search for sound
    '''
    
    audiofile, sampwidth, framerate = _openAudioFile(fn)

    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    audiofile.setpos(int(framerate*startTime))
    while currentSequenceNum < numSteps:
        numFrames = int(framerate * stepSize)
        waveData = audiofile.readframes(numFrames)

        if len(waveData) == 0:
            raise EndOfAudioData()
        
        actualNumFrames = int(len(waveData) / float(sampwidth))
        audioFrameList = struct.unpack("<"+"h"*actualNumFrames, waveData)
        
        rmsEnergy = _rms(audioFrameList)
        print rmsEnergy
        
        if ((findSilence == True and rmsEnergy < silenceThreshold) or
           (findSilence == False and rmsEnergy > silenceThreshold)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime


def naiveVAD(wavFN, silenceThreshold, stepSize, numSteps, startTime=0.0):
    
    endTime = findNextEvent(wavFN, startTime, silenceThreshold, 
                            stepSize, numSteps, findSilence=True)
    
    # Each iteration begins at a non-silence event and ends in a new silence event
    # (i.e. spans the interval of the non-silence)
    entryList = []
    try:
        while True:
            
            startTime = findNextEvent(wavFN, endTime, silenceThreshold, 
                                      stepSize, numSteps, findSilence=False)
            
            endTime = findNextEvent(wavFN, startTime, silenceThreshold, 
                                    stepSize, numSteps, findSilence=True)
            entryList.append( (startTime, endTime) )
            
    except (EndOfAudioData, wave.Error):
        pass # Stop processing
    
    return entryList
    

if __name__ == "__main__":

#     wavFN = "/Users/tmahrt/Desktop/avatar_corpus/01-140715_1356.wav"
#     origTGFN = "/Users/tmahrt/Desktop/avatar_corpus/01-140715_1421.TextGrid" 
#     tgFN = "/Users/tmahrt/Desktop/avatar_corpus/01-140715_1421_5.TextGrid"
#     firstStartTime = 135.37
#     labelStartIndex = 36
# 
    leftSilenceThreshold = 200
    rightSilenceThreshold = 220
    tmpStepSize = 0.05 # in seconds
    silenceNumSteps = 5 # 0.25 seconds (required Number of steps to be silence / noise)
    speakerNumSteps = 10 # 1 second (for 1 speaker)
    speakerStepSize = 1.00
    
#     print getRMSIntensity(wavFN, 8.5, 8.7)
#     print getRMSIntensity(wavFN, 18.68, 19.23)
#     print getRMSIntensity(wavFN, 19.2, 19.78)
#     autoCorrectTextgrid(wavFN, origTGFN, tgFN, firstStartTime, silenceThreshold, stepSize, numSteps,
#                         labelStartIndex=labelStartIndex)
    
#     outputTranscript(origTGFN)
    
    path = "/Users/tmahrt/Desktop/ECDL_data/october_10_2014/split_audio/cleaned"
    leftFN = ""
    rightFN = ""
    for name in ["test1"]:
        leftFN = join(path, name+"_L.wav")
        rightFN = join(path, name+"_R.wav")
        outputTGFN = join(path, name+".TextGrid")
        autosegmentStereoAudio(leftFN, rightFN, outputTGFN, leftSilenceThreshold, rightSilenceThreshold, 
                               tmpStepSize, silenceNumSteps, speakerNumSteps, 0)

