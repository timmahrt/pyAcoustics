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

    output = soundObj.pitch(method="ESPS",
                            minpitch=minPitch,
                            maxpitch=maxPitch)

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

    path = "/Users/tmahrt/Desktop/fire_new_audio_test"
    for name in utils.findFiles(path, filterExt=".wav", stripExt=True):
        tmpPitchList = extractPitch(join(path, name + ".wav"), 75, 450)
        tmpPitchList = [str(val) for val in tmpPitchList]
        
        with open(join(path, name + "_f0.csv"), "w") as fd:
            fd.write("\n".join(tmpPitchList))
