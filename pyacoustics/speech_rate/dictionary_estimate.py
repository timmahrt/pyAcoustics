'''
Created on Jan 28, 2015

@author: tmahrt
'''

import os
from os.path import join

from pyacoustics.utilities import utils
from pysle import isletool


def percentInside(startTime, endTime, cmprStartTime, cmprEndTime):
    
    if (float(startTime) <= float(cmprEndTime) and
            float(endTime) >= float(cmprStartTime)):

        leftEdge = cmprStartTime - startTime
        rightEdge = endTime - cmprEndTime
        
        if leftEdge < 0:
            leftEdge = 0
        if rightEdge < 0:
            rightEdge = 0
            
        retVal = 1 - ((rightEdge + leftEdge)) / (endTime - startTime)

    # No overlap
    else:
        retVal = 0

    return retVal


def manualPhoneCount(tgInfoPath, isleFN, outputPath, skipList=None):
    
    if skipList is None:
        skipList = []
    
    utils.makeDir(outputPath)
    
    isleDict = isletool.LexicalTool(isleFN)
    
    existFNList = utils.findFiles(outputPath, filterPaths=".txt")
    for fn in utils.findFiles(tgInfoPath, filterExt=".txt",
                              skipIfNameInList=existFNList):

        if os.path.exists(join(outputPath, fn)):
            continue
        print fn
        
        dataList = utils.openCSV(tgInfoPath, fn)
        outputList = []
        for start, stop, tmpLabel in dataList:
            if tmpLabel not in skipList:
                syllableCount, phoneCount = isletool.getNumPhones(isleDict,
                                                                  tmpLabel,
                                                                  maxFlag=True)
            else:
                syllableCount, phoneCount = 0, 0
            
            outputList.append("%d,%d" % (syllableCount, phoneCount))
        
        outputTxt = "\n".join(outputList)
        
        open(join(outputPath, fn), "w").write(outputTxt)
        

def manualPhoneCountForEpochs(manualCountsPath, tgInfoPath, epochPath,
                              outputPath):
    
    utils.makeDir(outputPath)
    
    skipList = utils.findFiles(outputPath, filterExt=".txt")
    for fn in utils.findFiles(tgInfoPath, filterExt=".txt",
                              skipIfNameInList=skipList):
        
        epochList = utils.openCSV(epochPath, fn)
        tgInfo = utils.openCSV(tgInfoPath, fn)
        manualCounts = utils.openCSV(manualCountsPath, fn)
        
        epochOutputList = []
        for epochNumber, epochStart, epochStop in epochList:
            epochStart, epochStop = float(epochStart), float(epochStop)
            
            # Find all of the intervals that are at least partially
            # contained within the current epoch
            epochSyllableCount = 0
            epochPhoneCount = 0
            speechDuration = 0
            for info, counts in utils.safeZip([tgInfo, manualCounts],
                                              enforceLength=True):
                start, stop, wordList = info
                start, stop = float(start), float(stop)
                
                syllableCount, phoneCount = counts
                syllableCount, phoneCount = float(syllableCount), float(phoneCount)
            
                # Accounts for intervals that straddle an epoch boundary
                multiplicationFactor = percentInside(start, stop,
                                                     epochStart, epochStop)
                
                speechDuration += (stop - start) * multiplicationFactor
                
                epochSyllableCount += syllableCount * multiplicationFactor
                epochPhoneCount += phoneCount * multiplicationFactor
            
            epochOutputList.append("%f,%f,%f" % (epochSyllableCount,
                                                 epochPhoneCount,
                                                 speechDuration))
        
        open(join(outputPath, fn), "w").write("\n".join(epochOutputList))




