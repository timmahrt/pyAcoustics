'''
Created on May 31, 2013

@author: timmahrt

Contains utilities for extracting, creating, and manipulating pitch files in
praat.
'''

import os
from os.path import join, splitext

import praatio

from pyacoustics.intensity_and_pitch import get_f0

from pyacoustics.signals import audio_scripts

from pyacoustics.morph.morph_utils import common
from pyacoustics.morph.morph_utils import plot_morphed_data
from pyacoustics.morph.morph_utils import morph_sequence

from pyacoustics.utilities import sequences
from pyacoustics.utilities import statistics
from pyacoustics.utilities import utils


class NotAllNamesUnique(Exception):
    
    def __init__(self, fn, nonUniqueNameList):
        super(NotAllNamesUnique, self).__init__()
        self.fn = fn
        self.nonUniqueNameList = nonUniqueNameList
        
    def __str__(self):
    
        retString = "The following labels in %s are not unique: %s  \n" + \
                    "No identical labels are allowed in a textgrid."
        return retString


def getPitchData(pitchTierPath, path, fromFN, toFN,
                 fromTG, toTG,
                 fromMinPitch, fromMaxPitch,
                 toMinPitch, toMaxPitch, loadPitchFlag, tierName):
    '''
    '''
    
    def savePitchTrack(pitchData, duration, fn):
        '''
        This is just for printing out the pitch data
        '''
        returnList = []

        pitchTierData = []
        for pitchDatum, time in pitchData:
            if pitchDatum == 0.0:
                continue
            pitchTierData.append((str(pitchDatum), str(time)))
            
            # This allows us to continue on with our script with zeros removed
            returnList.append((pitchDatum, time))
            
        name = os.path.splitext(fn)[0] + ".PitchTier"
        savePitchData(pitchTierData, 0, duration, pitchTierPath, name)
        
        return returnList
    
    if loadPitchFlag:
        
        fromPitchFN = os.path.splitext(fromFN)[0] + ".PitchTier"
        toPitchFN = os.path.splitext(toFN)[0] + ".PitchTier"
        
        # This is the raw data, undivided by labeled interval in the textgrids
        fromPitchDataWhole = praatio.readPitchTier(pitchTierPath,
                                                   fromPitchFN)[1]
        toPitchDataWhole = praatio.readPitchTier(pitchTierPath,
                                                 toPitchFN)[1]
        
    else:
        # Creates /fromFN.PitchTier/ in /fromPath+'pitchTiers'/
        fromPitchDataWhole = createPitchTierESPS(path, fromFN, fromMinPitch,
                                                 fromMaxPitch, True)
        toPitchDataWhole = createPitchTierESPS(path, toFN, toMinPitch,
                                               toMaxPitch, True)
        
        fromDuration = audio_scripts.getSoundFileDuration(join(path, fromFN))
        toDuration = audio_scripts.getSoundFileDuration(join(path, toFN))
        
        fromPitchDataWhole = savePitchTrack(fromPitchDataWhole, fromDuration,
                                            fromFN)
        toPitchDataWhole = savePitchTrack(toPitchDataWhole, toDuration,
                                          toFN)
        
    fromPitchData = []
    for blah in fromTG.tierDict[tierName].getMatchedData(fromPitchDataWhole):
        fromPitchData.append(blah)
        
    toPitchData = []
    for blah in toTG.tierDict[tierName].getMatchedData(toPitchDataWhole):
        toPitchData.append(blah)
                           
    return fromPitchData, toPitchData

    
def f0Morph(path, fromFN, toFN, numSteps, tierName, doPlotPitchSteps,
            fromMinPitch, fromMaxPitch, toMinPitch, toMaxPitch,
            loadPitchFlag,
            praatExe,
            praatScriptDir):
    '''
    Resynthesizes the pitch track from a source to a target wav file
    
    Occurs over a three-step process.
    '''

    fromName = splitext(fromFN)[0]
    toName = splitext(toFN)[0]

    fromDuration = audio_scripts.getSoundFileDuration(join(path, fromFN))

    fromTG = praatio.openTextGrid(join(path, fromName + ".TextGrid"))
    toTG = praatio.openTextGrid(join(path, toName + ".TextGrid"))

    # Iterative pitch tier data path
    stepPitchTierPath = join(path, "stepPitchTiers")

    scriptPath = join(path, "scriptPath")  # Generated praat scripts path
    pitchTierPath = join(path, "pitchTiers")  # Pitch tier data path
    stepOutputPath = join(path, "output")  # The final data will be output here
    
    for tmpPath in [scriptPath, pitchTierPath, stepPitchTierPath,
                    stepOutputPath]:
        utils.makeDir(tmpPath)
    
    # 1. Get the pitch tiers from the audio files
    fromPitchData, toPitchData = getPitchData(pitchTierPath, path,
                                              fromFN, toFN,
                                              fromTG, toTG,
                                              fromMinPitch, fromMaxPitch,
                                              toMinPitch, toMaxPitch,
                                              loadPitchFlag, tierName)

    # 2. Morph the fromData to the toData
    finalOutputList = morph_sequence.morphChunkedDataLists(fromPitchData,
                                                           toPitchData,
                                                           numSteps)

    fromPitchData = [row for subList in fromPitchData for row in subList]
    toPitchData = [row for subList in toPitchData for row in subList]
    
    # Save the pitch data (necessary for step 3)
    mergedDataList = []
    for i in xrange(0, len(finalOutputList)):
        outputPitchList = finalOutputList[i]
        outputFN = "%s_%d.PitchTier" % (toName, i)
        print("%s, %d" % (outputFN, len(finalOutputList)))
        savePitchData(outputPitchList, str(0), fromDuration,
                      stepPitchTierPath, outputFN)
        
        outputVals, outputTime = zip(*outputPitchList)
        mergedDataList.append((outputVals, outputTime))
    
    # Plot the generated contours
    if doPlotPitchSteps:
        fromVals, fromTime = zip(*fromPitchData)
        toVals, toTime = zip(*toPitchData)
            
        plot_morphed_data.plotF0((fromVals, fromTime),
                                 (toVals, toTime),
                                 mergedDataList,
                                 join(stepPitchTierPath,
                                      "%s_%d.png" % (fromName, 1)))
    
    # 3. Resynthesize in praat
    # Creates a series of /fromFN_i.wav/ files in /fromPath/
    psolaDict = {'num_steps': numSteps,
                 'input_name': fromName,
                 'output_name': fromName + ("_f0_%s_%d" %
                                            (tierName, numSteps - 1)),
                 'input_dir': path,
                 'pitch_dir': stepPitchTierPath,
                 'output_dir': stepOutputPath,
                 'pitch_lower_bound': fromMinPitch,
                 'pitch_upper_bound': fromMaxPitch,
                 }
    synthesisScriptPath = join(scriptPath, fromName + "_synthesisPitch.praat")
    resynthesizePitchScript = common.loadPraatTemplate("psolaPitch.praat",
                                                       praatScriptDir)
    open(synthesisScriptPath, "w").write(resynthesizePitchScript % psolaDict)
    common.runPraatScript(praatExe, synthesisScriptPath)


def createPitchTierPraat(praatExe, path, fn, outputPath):
    '''
    Uses praat to extract pitch data for each region in tgTier
    '''
    name = splitext(fn)[0]
    
    toPitchTierScript = common.loadPraatTemplate("extractPitchTier")
    toPitchTierScript = toPitchTierScript % {'input_dir': path,
                                             'input_name': name,
                                             'output_dir': outputPath}
    
    common.runPraatScript(praatExe, toPitchTierScript)
    
    pitchDataList = praatio.readPitchTier(outputPath, name + ".PitchTier")
     
    return pitchDataList


def createPitchTierESPS(fnPath, fn, minPitch, maxPitch, doFilter,
                        tg=None, tgTierName=None):
    '''
    Returns pitch information for each region in tgTier
    
    Each label in tgTier has a list in returnList where each of these
    lists contain two sublists--one containing f0 data and one containing
    timestamps
    '''
    fnFullPath = join(fnPath, fn)
    
    pitchDataList = get_f0.extractPitch(fnFullPath, minPitch, maxPitch)[0]
    pitchDataList = [float(pitchVal) for pitchVal in pitchDataList]
    
    # Trim the first three and last three samples from the file
    # -- these tend to be erronous readings (not sure how many samples to grab)
    numToCrop = 3
    pitchDataList = pitchDataList[numToCrop:-1 * numToCrop]
    
    if doFilter:
        pitchDataList = statistics.medianFilter(pitchDataList, 5, True)
    
    # Get the timestamps that co-occur with each pitch value
    # and get the pitch values
    duration = float(audio_scripts.getSoundFileDuration(fnFullPath))
    intervalDuration = duration / ((len(pitchDataList) + (numToCrop * 2)))
    valRange = xrange(numToCrop, len(pitchDataList) + numToCrop)
    indexTimes = [i * intervalDuration for i in valRange]
      
    dataList = zip(pitchDataList, indexTimes)
    
    # Treat the file as a whole
    if tg is None:
        returnList = dataList
    # Process individual portions of the file
    else:
        returnList = []
        for newDataList in tg.findMatchedData(dataList, tgTierName):
            returnList.append(newDataList)
    
    return returnList


def savePitchData(pitchTierData, startTime, endTime, outputPath, outputFN):

    newDataList = []
    for value, time in pitchTierData:
        newDataList.append((time, value))

    pitchTierData = [row for subList in newDataList for row in subList]
    pitchTierData = [str(val) for val in pitchTierData]
    
    pitchTierHeader = ['File type = "ooTextFile"',
                       'Object class = "PitchTier"',
                       '',
                       str(startTime),  # start time
                       str(endTime),  # end time
                       str(len(pitchTierData) / 2),  # Num Items
                       ]
    
    praatio.writePitchTier(outputPath, outputFN, pitchTierHeader,
                           pitchTierData)
