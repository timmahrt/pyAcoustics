'''
Created on July 28, 2015

@author: tmahrt

This code estimates the speech rate of a speaker by using Uwe Reichel's matlab
script for detecting syllable nuclei over some interval.
'''

from os.path import join

from pyacoustics.utilities import utils
from pyacoustics.utilities import matlab


def findSyllableNuclei(inputPath, outputPath, matlabEXE,
                       matlabScriptsPath, printCmd=False):
    '''
    Makes a file listing the syllable nuclei for each file in inputPath
    '''
    utils.makeDir(outputPath)
    
    pathList = [matlabScriptsPath,
                join(matlabScriptsPath, "nucleus_detection_matlab")]
    cmd = "detect_syllable_nuclei('%s', '%s');" % (inputPath, outputPath)
    matlab.runMatlabFunction(cmd, matlabEXE, pathList, printCmd)


def toAbsoluteTime(namePrefix, matlabOutputPath, startTimeList):
    '''
    Converts the sampled times from relative to absolute time
    
    The input may be split across a number of files.  This script assumes
    that files of the pattern <<namePrefix>><<nameSuffix>>.txt correspond
    to different parts of the same source file.
    
    namePrefix - name of the original wav file with no suffix
    speechRatePath - the path where the output of the matlab script is placed
    startTimeList - there needs to be one file here for each file in
                    speechRatePath with the pattern namePrefix
    
    Returns a list of lists where each sublist corresponds to the output of
    one file matching <<namePrefix>>
    '''
    # Load subset speech rate
    speechRateFNList = utils.findFiles(matlabOutputPath, filterExt=".txt",
                                       filterPattern=namePrefix)
    
    returnList = []
    for start, speechRateFN in utils.safeZip([startTimeList, speechRateFNList],
                                             enforceLength=True):
        speechRateList = utils.openCSV(matlabOutputPath,
                                       speechRateFN,
                                       valueIndex=0)
        speechRateList = [value for value in speechRateList if value != '']
        speechRateList = [str(float(start) + float(sampNum))
                          for sampNum in speechRateList]

        returnList.append(speechRateList)
    
    return returnList
    

def uweSyllableCountForInterval(startTime, stopTime, nucleiCenterList):

    countList = [timestamp for timestamp in nucleiCenterList
                 if timestamp >= startTime and timestamp <= stopTime]
    
    return len(countList)
