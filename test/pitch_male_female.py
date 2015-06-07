
import os
from os.path import join

from pyacoustics.intensity_and_pitch import praat_pi
from pyacoustics.utilities import utils

inputPath = "/Users/tmahrt/Desktop/ehp_force_align/subjects"

dataList = open(join(inputPath, "file_name_gender_list.txt"), "r").readlines()
dataList = [[item.strip() for item in row.split(",")] for row in dataList]


outputPath = "/Users/tmahrt/Desktop/ehp_force_align/subjects/pitchAndIntensity"
praatEXE = "/Applications/praat.App/Contents/MacOS/Praat"
praatScriptPath = "/Users/tmahrt/Dropbox/workspace/AcousticFeatureExtractionSuite/praatScripts"
sampleStep = 0.01
forceRegenerate = True

for inputFN, idNum, gender in dataList:
    name = os.path.splitext(inputFN)[0]
    
    assert(gender == "male" or gender == "female")
    if os.path.exists(join(outputPath, name+".txt")):
        continue
    
    if gender == "male":
        minPitch = 50
        maxPitch = 300
    else:
        minPitch = 75
        maxPitch = 450
    
    praat_pi.getPraatPitchAndIntensity(inputPath,
                                       inputFN,
                                       outputPath,
                                       praatEXE,
                                       praatScriptPath,
                                       minPitch,
                                       maxPitch,
                                       sampleStep,
                                       forceRegenerate)
