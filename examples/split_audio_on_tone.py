
import os
from os.path import join

from praatio import tgio
from praatio import pitch_and_intensity

from pyacoustics.speech_detection import split_on_tone
from pyacoustics.utilities import utils
from pyacoustics.signals import audio_scripts


def audiosplitOnTone(inputPath, fn, pitchPath, tgPath, subwavPath,
                     minPitch, maxPitch, toneFrequency, minEventDuration,
                     praatEXE, praatScriptPath, forceRegen,
                     generateWavs=False):
    
    utils.makeDir(pitchPath)
    utils.makeDir(tgPath)
    utils.makeDir(subwavPath)
    
    name = os.path.splitext(fn)[0]
    piSamplingRate = 100  # Samples per second

    # Extract pitch and find patterns in the file
    outputFN = os.path.splitext(fn)[0] + ".txt"
    sampleStep = 1 / float(piSamplingRate)
    motherPIList = pitch_and_intensity.audioToPI(inputPath, fn,
                                                 pitchPath, outputFN,
                                                 praatEXE,
                                                 minPitch, maxPitch,
                                                 sampleStep=sampleStep,
                                                 forceRegenerate=forceRegen)
    # entry = (time, pitchVal, intVal)
    pitchList = [float(entry[1]) for entry in motherPIList]
    timeDict = split_on_tone.splitFileOnTone(pitchList,
                                             piSamplingRate,
                                             toneFrequency,
                                             minEventDuration)

    # Output result as textgrid
    duration = audio_scripts.getSoundFileDuration(join(inputPath, fn))
    tg = tgio.Textgrid()
    for key in ['beep', 'speech', 'silence']:
        entryList = timeDict[key]
        tier = tgio.IntervalTier(key, entryList, 0, duration)
        tg.addTier(tier)
    tg.save(join(tgPath, name + ".TextGrid"))

    # Output audio portions between tones
    if generateWavs:
        split_on_tone.extractSubwavs(timeDict, inputPath, fn, subwavPath)


if __name__ == "__main__":
    _dataPath = "/Users/tmahrt/Dropbox/workspace/pyAcoustics/test/files"
    _pitchPath = join(_dataPath, "split_on_tone_pitch")
    _tgPath = join(_dataPath, "split_on_tone_textgrids")
    _wavOutputPath = join(_dataPath, "split_on_tone_subwavs")
    _fn = "tone_split_data.wav"
    _minPitch = 50
    _maxPitch = 450
    _toneFrequency = 330  # Actual frequency is 333
    _minEventDuration = 0.2
    _forceRegeneratePitch = False
    _generateWavs = True
    
    _praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
    _praatScriptPath = ("/Users/tmahrt/Dropbox/workspace/pyAcoustics/"
                        "praatScripts")

    audiosplitOnTone(_dataPath, _fn, _pitchPath, _tgPath, _wavOutputPath,
                     _minPitch, _maxPitch, _toneFrequency, _minEventDuration,
                     _praatEXE, _praatScriptPath, _forceRegeneratePitch,
                     _generateWavs)
    
    
    # Let's try the same code with an incorrect tone frequency
    _toneFrequency = 500
    _tgPath = join(_dataPath, "split_on_tone_textgrids_500hz_tone")
    _generateWavs = False

    audiosplitOnTone(_dataPath, _fn, _pitchPath, _tgPath, _wavOutputPath,
                     _minPitch, _maxPitch, _toneFrequency, _minEventDuration,
                     _praatEXE, _praatScriptPath, _forceRegeneratePitch,
                     _generateWavs)
