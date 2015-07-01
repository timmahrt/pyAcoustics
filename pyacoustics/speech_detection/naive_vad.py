
import wave

from pyacoustics.speech_detection import common


def _findNextEvent(sampleList, startTime, silenceThreshold, sampleFreq,
                   stepSize, numSteps, findSilence=True):
    '''
    
    if findSilence=False then search for sound
    '''
    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    while currentSequenceNum < numSteps:

        currentTime = startTime + i * stepSize
        nextTime = startTime + (i + 1) * stepSize

        audioFrameList = sampleList[int(round(currentTime * sampleFreq)):
                                    int(round(nextTime * sampleFreq))]
        
        if len(audioFrameList) == 0:
            raise common.EndOfAudioData()
        
        rmsEnergy = common.rms(audioFrameList)
        
        if ((findSilence is True and rmsEnergy < silenceThreshold) or
           (findSilence is False and rmsEnergy > silenceThreshold)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime


def naiveVAD(sampleList, silenceThreshold, sampleFreq,
             stepSize, numSteps, startTime=0.0):
    
    endTime = _findNextEvent(sampleList, startTime, silenceThreshold,
                             sampleFreq, stepSize, numSteps,
                             findSilence=True)
    
    # Each iteration begins at a non-silence event and ends in a new
    # silence event (i.e. spans the interval of the non-silence)
    entryList = []
    try:
        while True:
            
            startTime = _findNextEvent(sampleList, endTime, silenceThreshold,
                                       sampleFreq, stepSize, numSteps,
                                       findSilence=False)
            
            endTime = _findNextEvent(sampleList, startTime, silenceThreshold,
                                     sampleFreq, stepSize, numSteps,
                                     findSilence=True)
            entryList.append((startTime, endTime))
            
    except (common.EndOfAudioData, wave.Error):
        pass  # Stop processing
    
    return entryList
    

def getIntensityPercentile(sampleList, cutoffPercent):
    '''
    Returns the nth percent of energy represented in a dataset
    '''
    tmpSampleList = sorted(sampleList)
    
    return tmpSampleList[int(len(tmpSampleList) * cutoffPercent)]


def cropSilenceInEdges(sampleList, silenceThreshold, sampleFreq):
    '''
    Returns the left and right boundaries of the meaningful data in a wav file
    '''
    startI = 0
    while sampleList[startI] < silenceThreshold:
        startI += 1
    
    endI = len(sampleList) - 1
    while sampleList[endI] < silenceThreshold:
        endI -= 1
    
    startTime = startI * sampleFreq
    endTime = endI * sampleFreq
    
    return startTime, endTime
