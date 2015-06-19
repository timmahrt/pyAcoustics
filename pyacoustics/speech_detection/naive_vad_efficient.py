
import math
import struct
import wave

from pyacoustics.speech_detection import common


def findNextEvent(fn, startTime, silenceThreshold, stepSize,
                  numSteps, findSilence=True):
    '''
    
    if findSilence=False then search for sound
    '''
    
    audiofile, sampwidth, framerate = common.openAudioFile(fn)
    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    audiofile.setpos(int(framerate * startTime))
    while currentSequenceNum < numSteps:
        numFrames = int(framerate * stepSize)
        waveData = audiofile.readframes(numFrames)

        if len(waveData) == 0:
            raise common.EndOfAudioData()
        
        actualNumFrames = int(len(waveData) / float(sampwidth))
        audioFrameList = struct.unpack("<" + "h" * actualNumFrames, waveData)
        
        rmsEnergy = common.rms(audioFrameList)
        print(rmsEnergy)
        
        if ((findSilence is True and rmsEnergy < silenceThreshold) or
           (findSilence is False and rmsEnergy > silenceThreshold)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime


def naiveVAD(wavFN, silenceThreshold, stepSize, numSteps, startTime=0.0):
    
    endTime = findNextEvent(wavFN, startTime, silenceThreshold,
                            stepSize, numSteps, findSilence=True)
    
    # Each iteration begins at a non-silence event and ends in a new
    # silence event (i.e. spans the interval of the non-silence)
    entryList = []
    try:
        while True:
            
            startTime = findNextEvent(wavFN, endTime, silenceThreshold,
                                      stepSize, numSteps, findSilence=False)
            
            endTime = findNextEvent(wavFN, startTime, silenceThreshold,
                                    stepSize, numSteps, findSilence=True)
            entryList.append((startTime, endTime))
            
    except (common.EndOfAudioData, wave.Error):
        pass  # Stop processing
    
    return entryList
