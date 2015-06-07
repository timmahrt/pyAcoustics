
from pyacoustics.intensity_and_pitch import praat_pi
from pyacoustics.utilities import utils

inputPath = "/Users/tmahrt/Desktop/ehp_force_align/jennifer/blah"
outputPath = "/Users/tmahrt/Desktop/ehp_force_align/jennifer/pitchAndIntensity"
praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
praatScriptPath = "/Users/tmahrt/Dropbox/workspace/AcousticFeatureExtractionSuite/praatScripts"
minPitch = 75
maxPitch = 450
sampleStep = 0.01
forceRegenerate = True

for inputFN in utils.findFiles(inputPath, filterExt=".wav"):
    praat_pi.getPraatPitchAndIntensity(inputPath,
                                       inputFN,
                                       outputPath,
                                       praatEXE,
                                       praatScriptPath,
                                       minPitch,
                                       maxPitch,
                                       sampleStep,
                                       forceRegenerate)
