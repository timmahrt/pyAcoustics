'''
Created on Aug 23, 2014

@author: tmahrt
'''

import os
from os.path import join

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
            with open(durationFN, "w") as fd:
                fd.write(str(duration))
        except IOError:
            # If we don't have write permissions, there isn't anything we can
            # do, the user should still be able to get their data
            pass
    else:
        with open(durationFN, "r") as fd:
            duration = float(fd.read())
        
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
