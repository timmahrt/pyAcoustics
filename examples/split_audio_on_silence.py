
import os
from os.path import join

import datetime
now = datetime.datetime.now

from pyacoustics.intensity_and_pitch import praat_pi
from pyacoustics.speech_detection import naive_vad
from pyacoustics.signals import audio_scripts
from pyacoustics.utilities import utils
from pyacoustics.utilities import my_math

import praatio


def audiosplitSilence(inputPath, fn, outputPath, subwavPath,
                      minPitch, maxPitch, intensityPercentile,
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
    utils.makeDir(outputPath)
    utils.makeDir(subwavPath)
    
    name = os.path.splitext(fn)[0]
    
    piSamplingRate = 100  # Samples per second
    
    motherPIList = praat_pi.getPitch(inputPath, fn, outputPath, praatEXE,
                                     praatScriptPath, minPitch, maxPitch,
                                     sampleStep=1 / float(piSamplingRate),
                                     forceRegenerate=False)

    # entry = (time, pitchVal, intVal)
    motherPIList = [float(entry[2]) for entry in motherPIList]
    silenceThreshold = naive_vad.getIntensityPercentile(motherPIList,
                                                        intensityPercentile)
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
    tg = praatio.Textgrid()
    duration = audio_scripts.getSoundFileDuration(join(inputPath, fn))
    tier = praatio.IntervalTier("speech_tier", entryList, 0, duration)
    tg.addTier(tier)
    tg.save(join(outputPath, name + '.TextGrid'))

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
    _wavOutputPath = join(_dataPath, "output_wavs")
    _praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
    _praatScriptPath = ("/Users/tmahrt/Dropbox/workspace/pyAcoustics/"
                        "praatScripts")
    utils.makeDir(_wavOutputPath)
    _rootFolderName = os.path.splitext(os.path.split(_fn)[1])[0]
    _subwavOutputPath = join(_wavOutputPath, _rootFolderName)
    audiosplitSilence(_dataPath, _fn, _outputPath, _subwavOutputPath,
                      _minPitch, _maxPitch, _intensityPercentile,
                      _stepSize, _numSteps, _praatEXE, _praatScriptPath)
    
    # Changing the parameters used in silence detection can lead to
    # very different results
    _stepSize = 0.01
    _outputPath = join(_dataPath, "output_stepSize_0.01")
    audiosplitSilence(_dataPath, _fn, _outputPath, _subwavOutputPath,
                      _minPitch, _maxPitch, _intensityPercentile,
                      _stepSize, _numSteps, _praatEXE, _praatScriptPath)
