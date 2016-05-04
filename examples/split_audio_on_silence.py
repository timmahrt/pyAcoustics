
import os
from os.path import join

import datetime
now = datetime.datetime.now

from praatio import pitch_and_intensity

from pyacoustics.speech_detection import naive_vad
from pyacoustics.signals import audio_scripts
from pyacoustics.signals import data_fitting
from pyacoustics.utilities import utils
from pyacoustics.utilities import my_math

from praatio import tgio


def audiosplitSilence(inputPath, fn, tgPath, pitchPath, subwavPath,
                      minPitch, maxPitch,
                      stepSize, numSteps,
                      praatEXE, praatScriptPath,
                      generateWavs=False,
                      numSegmentsToExtract=None,):
    '''
    Extract the non-silence portions of a file
    
    minPitch - the speaker's minimum pitch
    maxPitch - the speaker's maximum pitch
    intensityPercentile - Given the distribution of intensity values in a file,
                            the intensity threshold to use is the one that
                            falls at /intensityPercentile/
                            Any intensity values less than the intensity
                            threshold will be considered silence.
                            I typically use a value between 0.2 or 0.3.
    stepSize - non-overlapping step size (in seconds)
    numSteps - number of consecutive blocks needed for a segment to be
                considered silence
                stepSize * numSteps is the smallest possible interval that
                can be considered silence/not-silence.
    praatEXE - fullpath to a praat executable.  On Windows use praatcon.exe.
                Other systems use praat
    praatScriptPath - location of the folder containing praat scripts that
                        is distributed with pyAcoustics
    numSegmentsToExtract - if not None remove all but the X loudest segments as
                            specified by /numSegmentsToExtract/.  Otherwise,
                            all non-silent segments are kept.
    generateWavs - if False, no wavefiles are extracted, but you can look at
                    the generated textgrids to see which wavefiles would have
                    been extracted
    '''
    utils.makeDir(tgPath)
    utils.makeDir(pitchPath)
    utils.makeDir(subwavPath)
    
    name = os.path.splitext(fn)[0]
    
    piSamplingRate = 100  # Samples per second
    sampleStep = 1 / float(piSamplingRate)
    outputFN = os.path.splitext(fn)[0] + ".txt"
    motherPIList = pitch_and_intensity.audioToPI(inputPath, fn,
                                                 pitchPath, outputFN,
                                                 praatEXE,
                                                 minPitch, maxPitch,
                                                 sampleStep=sampleStep,
                                                 forceRegenerate=False)

    # entry = (time, pitchVal, intVal)
    motherPIList = [float(entry[2]) for entry in motherPIList]
    
    # We need the intensity threshold to distinguish silence from speech/noise
    # Naively, we can extract this by getting the nth percent most intense
    # sound in the file naive_vad.getIntensityPercentile()
    # (but then, how do we determine the percent?)
    # Alternatively, we could consider the set of intensity values to be
    # bimodal -- silent values vs non-silent.  The best threshold is the one
    # that minimizes the overlap between the two distributions, obtained via
    # data_fitting.getBimodalValley()
#     silenceThreshold = naive_vad.getIntensityPercentile(motherPIList,
#                                                         intensityPercentile)
    silenceThreshold = data_fitting.getBimodalValley(motherPIList, doplot=True)
    print(silenceThreshold)
    entryList = naive_vad.naiveVAD(motherPIList, silenceThreshold,
                                   piSamplingRate, stepSize, numSteps)
    entryList = [(time[0], time[1], str(i))
                 for i, time in enumerate(entryList)]

    # Filter out quieter sounds if necessary
    if numSegmentsToExtract is not None:
        
        # Get the rms energy of each non-silent region
        rmsEntryList = []
        for i, entry in enumerate(entryList):
            intList = motherPIList[int(entry[0] * piSamplingRate):
                                   int(entry[1] * piSamplingRate)]
            
            rmsVal = my_math.rms(intList)
            rmsEntryList.append((rmsVal, entry))
    
        rmsEntryList.sort()  # Sort by energy
        entryList = [rmsTuple[1]
                     for rmsTuple in rmsEntryList[:numSegmentsToExtract]]
        entryList.sort()  # Sort by time

    # Create the textgrid
    tg = tgio.Textgrid()
    duration = audio_scripts.getSoundFileDuration(join(inputPath, fn))
    tier = tgio.IntervalTier("speech_tier", entryList, 0, duration)
    tg.addTier(tier)
    tg.save(join(tgPath, name + '.TextGrid'))

    if generateWavs is True:
        for i, entry in enumerate(entryList):
            subwavOutputFN = join(subwavPath, name + "_" + str(i) + ".wav")
            audio_scripts.extractSubwav(join(inputPath, fn),
                                        subwavOutputFN,
                                        entry[0], entry[1],
                                        singleChannelFlag=True)
        

if __name__ == "__main__":
    _minPitch = 50
    _maxPitch = 450
    _intensityPercentile = 0.3
    _stepSize = 0.1
    _numSteps = 5
    
    _fn = "introduction.wav"
    _dataPath = join('/Users/tmahrt/Dropbox/workspace/pyAcoustics/test/files')
    _outputPath = join(_dataPath, "output_stepSize_0.1")
    _tgPath = join(_dataPath, "splitAudio_silence_stepSize_0.1")    
    _pitchPath = join(_dataPath, "pitch")
    _wavOutputPath = join(_dataPath, "output_wavs")
    _praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
    _praatScriptPath = ("/Users/tmahrt/Dropbox/workspace/pyAcoustics/"
                        "praatScripts")
    utils.makeDir(_wavOutputPath)
    _rootFolderName = os.path.splitext(os.path.split(_fn)[1])[0]
    _subwavOutputPath = join(_wavOutputPath, _rootFolderName)
    audiosplitSilence(_dataPath, _fn, _tgPath, _pitchPath, _subwavOutputPath,
                      _minPitch, _maxPitch,
                      _stepSize, _numSteps, _praatEXE, _praatScriptPath)
    
    # Changing the parameters used in silence detection can lead to
    # very different results
    _stepSize = 0.025
    _numSteps = 10
    _tgPath = join(_dataPath, "splitAudio_silence_stepSize_0.025")
    audiosplitSilence(_dataPath, _fn, _tgPath, _pitchPath, _subwavOutputPath,
                      _minPitch, _maxPitch,
                      _stepSize, _numSteps, _praatEXE, _praatScriptPath)
