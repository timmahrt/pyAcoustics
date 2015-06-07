'''
A Python implementation of ESPS's getF0 function

The implementation is part of tkSnack.  As I recall, it is a bit
cumbersome to install, although there are python distributions,
like ActiveState, which come with it preinstalled.  For more information,
visit the snack website:
http://www.speech.kth.se/snack/
'''
import os
from os.path import join

import Tkinter
root = Tkinter.Tk()
import tkSnack
tkSnack.initializeSnack(root)


from rpt_feature_suite.utilities import utils

MALE = "male"
FEMALE = "female"

SAMPLE_FREQ = 100


def extractPitch(fnFullPath, minPitch, maxPitch):
    '''
    
    Former default pitch values: male (50, 350); female (75, 450)
    '''
        
    soundObj = tkSnack.Sound(load=fnFullPath)

    output = soundObj.pitch(method="ESPS", minpitch=minPitch, maxpitch=maxPitch)

    pitchList = []
    for value in output:

        value = value[0]

        if value == 0:
            value = int(value)
        pitchList.append(value)
    
    return pitchList, SAMPLE_FREQ


def getPitchAtTime(pitchList, startTime, endTime):
    
    startIndex = int(startTime * SAMPLE_FREQ)
    endIndex = int(endTime * SAMPLE_FREQ)

    return pitchList[startIndex:endIndex]


if __name__ == "__main__":
    
#     from analysis import statistics
#     path = "/Users/timmahrt/Desktop/intonation_talk/cleaned/mary_statement.wav"
#     path2 = "/Users/timmahrt/Desktop/intonation_talk/cleaned/mary_question.wav"
#     
#     path = "/Users/tmahrt/Dropbox/matlab/tmp/CSDP_10_short.wav"
#     
#     f0Data = extractPitch(path, 50, 350)
#     f0Data = [float(val) for val in f0Data]
#     f0Data = statistics.medianFilter(f0Data, 5, True)
#     from praat import plotMorphedData
#     
#     f0Data2 = extractPitch(path2, 50, 350) 
#     f0Data2 = [float(val) for val in f0Data2]
#     f0Data2 = statistics.medianFilter(f0Data2, 5, True)
#     
#     path = "/Users/timmahrt/Desktop/intonation_talk/cleaned/tones.png"
# #     plotMorphedData.plotSinglePitchTrack(f0Data, path)
#     plotMorphedData.plotTwoPitchTracks(f0Data, f0Data2, path)
# 
#     from signals.timeAlign import dtw
#     from os.path import join
#     dtw.getWarpedValues(f0Data, f0Data2, join("/Users/timmahrt/Desktop/intonation_talk/cleaned/", "1_vs_2.png"))


    path = "/Users/tmahrt/Desktop/fire_new_audio_test"
    for name in utils.findFiles(path, filterExt=".wav", stripExt=True):
        pitchList = extractPitch(join(path, name+".wav"), 75, 450)
        pitchList = [str(val) for val in pitchList]
        open(join(path, name+"_f0.csv"), "w").write("\n".join(pitchList))


