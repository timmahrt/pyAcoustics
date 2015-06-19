'''
Created on Aug 23, 2014

@author: tmahrt
'''

import os
from os.path import join

import math
import struct
import wave
import audioop

from pyacoustics.utilities import utils


def loadWavFile(wavFN):
    
    sampWidthDict = {1: 'b', 2: 'h', 4: 'i', 8: 'q'}
    audiofile = wave.open(wavFN, "r")
    
    params = audiofile.getparams()
    sampwidth = params[1]
    nframes = params[3]
    
    byteCode = sampWidthDict[sampwidth]
    waveData = audiofile.readframes(nframes)
    audioFrameList = struct.unpack("<" + byteCode * nframes, waveData)
    
    return audioFrameList, params


def resampleAudio(newSampleRate, inputPath):
    
    outputPath = join(inputPath, "resampled_wavs")
    utils.makeDir(outputPath)
    
    for fn in utils.findFiles(inputPath, filterExt=".wav"):
        soxCmd = "%s %s -r %f %s rate -v 96k" % ("/opt/local/bin/sox",
                                                 join(inputPath, fn),
                                                 newSampleRate,
                                                 join(outputPath, fn))
        os.system(soxCmd)
        

def getSerializedFileDuration(fn):
    name = os.path.splitext(fn)[0]
    durationFN = name + "_duration.txt"
    if not os.path.exists(durationFN):
        duration = getSoundFileDuration(fn)
        try:
            open(durationFN, "w").write(str(duration))
        except IOError:
            # If we don't have write permissions, there isn't anything we can
            # do, the user should still be able to get their data
            pass
    else:
        duration = float(open(durationFN, "r").read())
        
    return duration


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
    

def getParams(fn):
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    
    return params


def reduceToSingleChannel(fn, outputFN, leftFactor=1, rightFactor=0):
    
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    sampwidth = params[1]
    nframes = params[3]
    audioFrames = audiofile.readframes(nframes)
    
    monoAudioFrames = audioop.tomono(audioFrames, sampwidth,
                                     leftFactor, rightFactor)
    params = tuple([1, ] + list(params[1:]))
    
    outputAudiofile = wave.open(outputFN, "w")
    outputAudiofile.setparams(params)
    outputAudiofile.writeframes(monoAudioFrames)


def modifySampleWidth(fn, outputFN, newSampleWidth):
    
    sampWidthDict = {1: 'b', 2: 'h', 4: 'i', 8: 'q'}
    
    audiofile = wave.open(fn, "r")
    params = audiofile.getparams()
    sampwidth = params[1]
    nframes = params[3]
    waveData = audiofile.readframes(nframes)
    
    sampleCode = sampWidthDict[sampwidth]
    newSampleCode = sampWidthDict[newSampleWidth]
    
    audioFrameList = struct.unpack("<" + sampleCode * nframes, waveData)
    outputByteStr = struct.pack("<" + newSampleCode * nframes, *audioFrameList)
    
    if newSampleWidth is not None:
        params = list(params[:2]) + [newSampleWidth, ] + list(params[3:])
        params = tuple(params)
    
    outputAudiofile = wave.open(outputFN, "w")
    outputAudiofile.setparams(params)
    outputAudiofile.writeframes(outputByteStr)


def monoToStereo(fnL, fnR, outputFN, lfactor=1.0, rfactor=1.0):
    '''
    Given two audio files, combines them into a stereo audio file
    
    Derived mostly from the official python documentation
    https://docs.python.org/2/library/audioop.html
    '''
    
    def _monoToStereo(fn, leftBalance, rightBalance):
        audiofile = wave.open(fn, "r")
        params = audiofile.getparams()
        sampwidth = params[1]
        nframes = params[3]
        
        waveData = audiofile.readframes(nframes)
        sample = audioop.tostereo(waveData, sampwidth,
                                  leftBalance, rightBalance)
    
        return sample, params
    
    lsample, params = _monoToStereo(fnL, lfactor, 1 - lfactor)
    rsample = _monoToStereo(fnR, 1 - rfactor, rfactor)[0]

    sampwidth, framerate, nframes, comptype, compname = params[1:]
    
    stereoSamples = audioop.add(lsample, rsample, sampwidth)
    
    outputAudiofile = wave.open(outputFN, "w")

    params = [2, sampwidth, framerate, nframes, comptype, compname]
    outputAudiofile.setparams(params)
    outputAudiofile.writeframes(stereoSamples)


def splitStereoAudio(path, fn, outputPath=None):
    
    if outputPath is None:
        outputPath = join(path, "split_audio")

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
    
    name = os.path.splitext(fn)[0]
    
    fnFullPath = join(path, fn)
    leftOutputFN = join(outputPath, "%s_L.wav" % name)
    rightOutputFN = join(outputPath, "%s_R.wav" % name)
    
    audiofile = wave.open(fnFullPath, "r")

    params = audiofile.getparams()
    sampwidth = params[1]
    nframes = params[3]
    audioFrames = audiofile.readframes(nframes)
    
    for leftFactor, rightFactor, outputFN in ((1, 0, leftOutputFN),
                                              (0, 1, rightOutputFN)):
        
        monoAudioFrames = audioop.tomono(audioFrames, sampwidth,
                                         leftFactor, rightFactor)
        params = tuple([1, ] + list(params[1:]))
        
        outputAudiofile = wave.open(outputFN, "w")
        outputAudiofile.setparams(params)
        outputAudiofile.writeframes(monoAudioFrames)


def getSubwav(fn, startT, endT, singleChannelFlag):
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    nchannels = params[0]
    sampwidth = params[1]
    framerate = params[2]

    # Extract the audio frames
    audiofile.setpos(int(framerate * startT))
    audioFrames = audiofile.readframes(int(framerate * (endT - startT)))
    
    # Convert to single channel if needed
    if singleChannelFlag is True and nchannels > 1:
        audioFrames = audioop.tomono(audioFrames, sampwidth, 1, 0)
        nchannels = 1
    
    return audioFrames
    
    
def extractSubwav(fn, outputFN, startT, endT, singleChannelFlag):
    
    audiofile = wave.open(fn, "r")
    params = audiofile.getparams()
    nchannels = params[0]
    sampwidth = params[1]
    framerate = params[2]
    comptype = params[4]
    compname = params[5]

    audioFrames = getSubwav(fn, startT, endT, singleChannelFlag)
    
    if singleChannelFlag is True and nchannels > 1:
        nchannels = 1
    
    outParams = [nchannels, sampwidth, framerate,
                 len(audioFrames), comptype, compname]
    
    outWave = wave.open(outputFN, "w")
    outWave.setparams(outParams)
    outWave.writeframes(audioFrames)


def findSilences(fn, silenceRMSThreshold, startTime=0):
    '''
    
    '''
    silenceList = []
    
    # Seed the search - we don't know if the audio begins with noise or silence
    findSilence = False
    firstEventTime = findNextEvent(fn, startTime, silenceRMSThreshold,
                                   findSilence)
    if firstEventTime == 0:
        findSilence = True
        firstEventTime = findNextEvent(fn, startTime, silenceRMSThreshold,
                                       findSilence)
    else:
        silenceList.append((0, firstEventTime))
    
    # Find all of the silences until the end of the file
    currentTime = firstEventTime
    while True:
        findSilence = not findSilence
        endTime = findNextEvent(fn, currentTime, silenceRMSThreshold,
                                findSilence)
        if findSilence is True:
            silenceList.append((currentTime, endTime))
        currentTime = endTime
        
    return silenceList
        
    
def findNextEvent(fn, startTime, silenceThreshold, findSilence=True):
    '''
    Accumulates wavdata until it hits the next silence/noise
    
    if findSilence=False then search for sound
    '''
    
    stepSize = 0.15  # in seconds
    numSteps = 3  # Number of steps required to be silence / noise
    
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    framerate = params[2]
    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    audiofile.setpos(int(framerate * startTime))
    while currentSequenceNum < numSteps:
        audioFrameList = audiofile.readframes(int(framerate * stepSize))

        rmsEnergy = _rms(audioFrameList)
        if ((findSilence is True and rmsEnergy < silenceThreshold) or
           (findSilence is False and rmsEnergy > silenceThreshold)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime


def findQuietestSilence(fn, duration, windowDuration):
    '''
    Finds the quietest silence of length /duration/
    
    The actual duration of the quietest silence will not be the same
    as /duration/
    
    duration and windowDuration are both in seconds
    '''
    
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    sampwidth = params[1]
    framerate = params[2]
    
    # Number of blocks that will fit into the duration
    blockSize = int(framerate * windowDuration)
    rmsIntensityList = []
    while True:
        waveData = audiofile.readframes(blockSize)
        if len(waveData) == 0:
            break

        actualNumFrames = int(len(waveData) / float(sampwidth))
        audioFrameList = struct.unpack("<" + "h" * actualNumFrames, waveData)
        
        rmsIntensityList.append(_rms(audioFrameList))
    
    # A 'block' here refers to one segment that is /duration/ long
    numSamplesPerBlock = int(round((duration) / windowDuration))
    
    # Calculate the sum of RMS values for every chunk
    sumList = [sum(rmsIntensityList[i:i + numSamplesPerBlock])
               for i in xrange(0, len(rmsIntensityList) - numSamplesPerBlock)]
    
    # Select the quietest chunk and convert to time
    startIndex = sumList.index(min(sumList))
    endIndex = startIndex + numSamplesPerBlock

    startTime = (startIndex * blockSize) / float(framerate)
    endTime = (endIndex * blockSize) / float(framerate)

    # The mean energy for this region
    meanRMSEnergy = sumList[startIndex]
    
    actualSilenceDuration = endTime - startTime
    
    return startTime, endTime, meanRMSEnergy, actualSilenceDuration


def findIntensityThreshold(fn, windowDuration, percentile):
    '''
    
    
    /percentile/ - percentage.  A value between 0 and 1.
    '''
    audiofile = wave.open(fn, "r")
    
    params = audiofile.getparams()
    sampwidth = params[1]
    framerate = params[2]
    
    # Number of blocks that will fit into the duration
    blockSize = int(framerate * windowDuration)
    rmsIntensityList = []
    while True:
        waveData = audiofile.readframes(blockSize)
        if len(waveData) == 0:
            break

        actualNumFrames = int(len(waveData) / float(sampwidth))
        audioFrameList = struct.unpack("<" + "h" * actualNumFrames, waveData)
        
        rmsIntensityList.append(_rms(audioFrameList))
    
    rmsIntensityList.sort()
    
    return rmsIntensityList[int(len(rmsIntensityList) * percentile)]


def _rms(audioFrameList):
    audioFrameList = [val ** 2 for val in audioFrameList]
    meanVal = sum(audioFrameList) / len(audioFrameList)
    return math.sqrt(meanVal)
