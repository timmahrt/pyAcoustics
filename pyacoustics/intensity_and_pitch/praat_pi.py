# coding: utf-8
'''
Created on Oct 20, 2014

@author: tmahrt

To be used in conjunction with get_pitch_and_intensity.praat
'''

import os
from os.path import join
import sys
import subprocess
import math

import praatio

from pyacoustics.utilities import filters
from pyacoustics.utilities import utils
from pyacoustics.utilities import my_math


def getPitch(inputPath, inputFN, outputPath, praatEXE,
             praatScriptPath, minPitch, maxPitch,
             sampleStep=0.01, forceRegenerate=True):
    '''
    
    
    male: minPitch=50; maxPitch=350
    female: minPitch=75; maxPitch=450
    
    mac: praatPath=/Applications/praat.App/Contents/MacOS/Praat
    '''
    
    utils.makeDir(outputPath)
    
    outputFN = os.path.splitext(inputFN)[0] + '.txt'
    
    firstTime = not os.path.exists(join(outputPath, outputFN))
    if firstTime or forceRegenerate is True:
        
        # Warn user that this will likely not work if they are using windows
        if sys.platform.startswith('win'):  # Using windows
            if "praatcon.exe" not in praatEXE:
                print("Variable /praatEXE/ needs to point to praatcon.exe"
                      "on Windows, not praat.exe")
        
        # The praat script uses append mode, so we need to clear any prior
        # result
        if os.path.exists(join(outputPath, outputFN)):
            os.remove(join(outputPath, outputFN))
        
        # Final slashes required
        inputPath = join(inputPath, '')
        outputPath = join(outputPath, '')
        
        script = join(praatScriptPath,
                      "get_pitch_and_intensity_via_python.praat")
        scriptTxt = open(script, "r").read()
        
        scriptTxt = scriptTxt % {'input_directory': inputPath,
                                 'output_directory': outputPath,
                                 'file_name': inputFN,
                                 'sample_step': sampleStep,
                                 'min_pitch': minPitch,
                                 'max_pitch': maxPitch}
        
        tmpScript = join(outputPath,
                         "get_pitch_and_intensity_via_python_tmp.praat")
        open(tmpScript, "w").write(scriptTxt)
        
        myProcess = subprocess.Popen([praatEXE, tmpScript])
        if myProcess.wait():
            exit()
    
    return loadPitchAndTime(outputPath, outputFN)


def loadPitchAndTime(rawPitchDir, fn):
    '''
    For reading the output of get_pitch_and_intensity
    '''
    name = os.path.splitext(fn)[0]
    
    try:
        data = open(join(rawPitchDir, fn), "rU").read()
    except IOError:
        print("No pitch track for: %s" % name)
        raise
        
    dataList = data.splitlines()
    
    dataList = [row.split(',') for row in dataList if row != '']
    
    newDataList = []
    for time, f0Val, intensity in dataList:
        time = float(time)
        if '--' in f0Val:
            f0Val = 0.0
        else:
            f0Val = float(f0Val)
            
        if '--' in intensity:
            intensity = 0.0
        else:
            intensity = float(intensity)
        
        newDataList.append((time, f0Val, intensity))

    dataList = newDataList

    return dataList


def extractPraatPitch(intensityAndPitchPath, textgridPath, tierName,
                      outputPath, nullLabel=""):
    
    utils.makeDir(outputPath)
       
    for fn in utils.findFiles(intensityAndPitchPath, filterExt=".txt"):
        
        dataList = loadPitchAndTime(intensityAndPitchPath, fn)
        
        name = os.path.splitext(fn)[0]
        
        tgFN = join(textgridPath, name + ".TextGrid")
        if not os.path.exists(tgFN):
            continue
        tg = praatio.openTextGrid(tgFN)
        tier = tg.tierDict[tierName]
       
        pitchData = []
        for valueList, label, _, _ in getValuesForIntervals(dataList,
                                                            tier.entryList):
            f0Values = [f0Val for _, f0Val, _ in valueList]
            label = label.strip()
            if label == "" or label == nullLabel:
                continue
            pitchData.append(getPitchMeasures(f0Values, name,
                                              label, True, True))
        
        open(join(outputPath, "%s.txt" % name),
             "w").write("\n".join(pitchData))


def extractRMSIntensity(intensityAndPitchPath, textgridPath, tierName,
                        outputPath, nullLabel=""):
    
    utils.makeDir(outputPath)
    
    for fn in utils.findFiles(intensityAndPitchPath, filterExt=".txt"):
        
        dataList = loadPitchAndTime(intensityAndPitchPath, fn)
        
        name = os.path.splitext(fn)[0]
        
        tgFN = join(textgridPath, name + ".TextGrid")
        if not os.path.exists(tgFN):
            continue
        tg = praatio.openTextGrid(join(textgridPath, name + ".TextGrid"))
        tier = tg.tierDict[tierName]
        
        print(fn)
        
        rmsIntensityList = []
        for valueList, label, _, _ in getValuesForIntervals(dataList,
                                                            tier.entryList):
            intensityVals = [intensityVal for _, _, intensityVal
                             in valueList]
        
            intensityVals = [intensityVal for intensityVal in intensityVals
                             if intensityVal != 0.0]
                    
            label = label.strip()
            if label == "" or label == nullLabel:
                continue
            
            rmsIntensity = 0
            if len(intensityVals) != 0:
                rmsIntensity = my_math.rms(intensityVals)
            
            rmsIntensityList.append(str(rmsIntensity))
    
        open(join(outputPath, "%s.txt" % name),
             "w").write("\n".join(rmsIntensityList))
        
        
def getValuesForIntervals(dataList, entryList):
    for start, stop, label in entryList:
        
        subDataList = getAllValuesInTime(start, stop, dataList)
        if subDataList == []:
            print("No f0 or intensity data for interval")
            print("%s, %s, %f, %f" %
                  (",".join(subDataList), label, start, stop))
        
        yield subDataList, label, start, stop
        
        
def getAllValuesInTime(startTime, stopTime, dataTuple):
    
    returnTuple = []
    for time, pitchVal, intensityVal in dataTuple:
        if time >= startTime and time <= stopTime:
            returnTuple.append((time, pitchVal, intensityVal))
            
    return returnTuple


def getPitchMeasures(f0Values, name, label,
                     medianFilterWindowSize=None,
                     filterZeroFlag=False):
    
    if medianFilterWindowSize is not None:
        f0Values = filters.medianFilter(f0Values, medianFilterWindowSize,
                                        useEdgePadding=True)
        
    if filterZeroFlag:
        f0Values = [f0Val for f0Val in f0Values if int(f0Val) != 0]
    
    if len(f0Values) == 0:
        myStr = u"No pitch data for file: %s, label: %s" % (name, label)
        print(myStr.encode('ascii', 'replace'))
        counts = 0
        meanF0 = 0
        maxF0 = 0
        minF0 = 0
        rangeF0 = 0
        
        variance = 0
        std = 0
    else:
        counts = float(len(f0Values))
        meanF0 = sum(f0Values) / counts
        maxF0 = max(f0Values)
        minF0 = min(f0Values)
        rangeF0 = maxF0 - minF0
    
        variance = sum([(val - meanF0) ** 2 for val in f0Values]) / counts
        std = math.sqrt(variance)
            
    return "%f, %f, %f, %f, %f, %f" % (meanF0, maxF0, minF0,
                                       rangeF0, variance, std)


def medianFilter(f0Path, outputPath, windowSize):
    
    # windowSize must be odd
    assert(windowSize % 2 != 0)
    
    utils.makeDir(outputPath)
    
    for fn in utils.findFiles(f0Path, filterExt=".txt"):
        valueList = utils.openCSV(f0Path, fn)
        
        f0List = [float(row[1]) if row[1] != "--undefined--" else 0
                  for row in valueList]  # time, f0Val, intensityVal
        f0Filtered = filters.medianFilter(f0List, windowSize,
                                          useEdgePadding=True)
        
        outputList = ["%s,%0.3f,%s" % (row[0], f0Val, row[2])
                      for row, f0Val in zip(*[valueList, f0Filtered])]
        open(join(outputPath, fn), "w").write("\n".join(outputList) + "\n")
