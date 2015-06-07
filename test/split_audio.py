
import os
from os.path import join

from pyacoustics.intensity_and_pitch import praat_pi
from pyacoustics.speech_detection import naive_vad
from pyacoustics.speech_detection import naive_vad_efficient
from pyacoustics.speech_detection import split_on_tone
from pyacoustics.signals import audio_scripts
from pyacoustics.utilities import utils
from pyacoustics.utilities import my_math

import praatio
# from pyacoustics.speech_detection import naive_vad_efficient

praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
praatScriptPath = "/Users/tmahrt/Dropbox/workspace/AcousticFeatureExtractionSuite/praatScripts"


def audiosplitOnTone(inputPath, fn, outputPath, minPitch, maxPitch):
    
    utils.makeDir(outputPath)
    
    piSamplingRate = 100 # Samples per second
    stepSize = 0.01 # In seconds
    numSteps = 5 # stepSize * numSteps = smallest possible 'silence' or 'speech act'

    motherPIList = praat_pi.getPraatPitchAndIntensity(inputPath, fn, outputPath, praatEXE,
                                  praatScriptPath, minPitch, maxPitch,
                                  sampleStep=1/float(piSamplingRate), forceRegenerate=False)
    pitchList = [float(pitchVal) for time, pitchVal, intVal in motherPIList]
    split_on_tone.splitFileOnTone(inputPath, fn, pitchList, piSamplingRate, createSubwavs=True,
                                  eventDurationThreshold=0.2)
    
                    
def audiosplitSilence(inputPath, fn, outputPath, subwavPath, minPitch, maxPitch):
    '''
    Extract the non-silence portions of a file
    '''
    utils.makeDir(outputPath)
    utils.makeDir(subwavPath)
    
    name = os.path.splitext(fn)[0]
    
    piSamplingRate = 100 # Samples per second
    stepSize = 0.01 # In seconds
    numSteps = 5 # stepSize * numSteps = smallest possible 'silence' or 'speech act'

    motherPIList = praat_pi.getPraatPitchAndIntensity(inputPath, fn, outputPath, praatEXE,
                                  praatScriptPath, minPitch, maxPitch,
                                  sampleStep=1/float(piSamplingRate), forceRegenerate=False)
    motherPIList = [float(intVal) for time, pitchVal, intVal in motherPIList]
    silenceThreshold = naive_vad.getIntensityPercentile(motherPIList,
                                                        0.30)
    entryList = naive_vad.naiveVAD(motherPIList, silenceThreshold, piSamplingRate, stepSize, numSteps)
    entryList = [(time[0], time[1], str(i)) for i, time in enumerate(entryList)]

    tg = praatio.Textgrid()
    tier = praatio.IntervalTier("speech_tier", entryList, 0, audio_scripts.getSoundFileDuration(join(inputPath, fn)))
    tg.addTier(tier)
    tg.save( join(outputPath, name+'.TextGrid'))

    rmsEntryList = []
    for i, entry in enumerate(entryList):
        intList = motherPIList[int(entry[0] * piSamplingRate):
                               int(entry[1] * piSamplingRate)]
        
        rmsVal = my_math.rms(intList)
        rmsEntryList.append((rmsVal, entry))
        
    rmsEntryList.sort() # Sort by energy
    entryList = [entry for rms, entry in rmsEntryList[-13:]]
    entryList.sort() # Sort by time

    for i, entry in enumerate(entryList):
        audio_scripts.extractSubwav(join(inputPath, fn), 
                                    join(subwavPath, name+"_"+str(i)+".wav"),
                                    entry[0], entry[1], singleChannelFlag=True)
        


dataPath = "/Users/tmahrt/Desktop/thesis/2015-01-26/"
outputPath = join(dataPath, "tmp")
wavOutputPath = join(dataPath, "output_wavs")
fn = "tim_recordings_Jan_27.wav"
minPitch = 50
maxPitch = 450

# This doesn't seem to work
# audiosplitOnTone(dataPath, fn, outputPath, minPitch, maxPitch)

dataPath = "/Users/tmahrt/Desktop/ehp_force_align/subjects/output_wavs2"
outputPath = join(dataPath, "tmp")
wavOutputPath = join(dataPath, "output_wavs")
# utils.makeDir(wavOutputPath)
for fn in utils.findFiles(dataPath, filterExt=".wav"):
    name = os.path.splitext(os.path.split(fn)[1])[0]
    subwavOutputPath = join(wavOutputPath, name)
#     audiosplitSilence(dataPath, fn, outputPath, subwavOutputPath, minPitch, maxPitch)
    duration = audio_scripts.getSoundFileDuration(join(dataPath, fn))
    tg = praatio.Textgrid()
    tier = praatio.IntervalTier("speech_segments", [], 0, duration)
