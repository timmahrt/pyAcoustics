'''
Created on Jun 5, 2013

@author: timmahrt
'''

import os
from os.path import join
import copy

import praatio

from pyacoustics.morph.morph_utils import common
from pyacoustics.utilities import utils
from pyacoustics.signals import audio_scripts
from pyacoustics.morph.morph_utils import plot_morphed_data

# This value is used to differentiate a praat interval boundary that marks
# the start of one region and the end of another.
PRAAT_TIME_DIFF = 0.000001


class NoLabeledRegionFoundException(Exception):
    
    def __init__(self, tgFN):
        super(NoLabeledRegionFoundException, self).__init__()
        self.tgFN = tgFN
        
    def __str__(self):
        return "No labeled region fitting the specified criteria for tg: " + \
            self.tgFN
    

def _psolaDuration(ratioTupleList, fromWavDuration, timeDiff, path, fromFN,
                   numSteps, tierName, fromMinPitch, fromMaxPitch,
                   outputFolder, praatExe):
    
    # Prep output directories
    outputPath = join(path, outputFolder)
    utils.makeDir(outputPath)
    
    scriptPath = join(path, "scripts")
    utils.makeDir(scriptPath)
    
    # Constants
    fromName = os.path.splitext(fromFN)[0]
    
    interpRatioTupleList = copy.deepcopy(ratioTupleList)
    # No need to stretch out any pauses at the beginning
    if interpRatioTupleList[0][0] != 0:
        tmpVar = (0, interpRatioTupleList[0][0] - timeDiff, 1)
        interpRatioTupleList.insert(0, tmpVar)

    # Or the end
    if interpRatioTupleList[-1][1] < fromWavDuration:
        interpRatioTupleList.append((interpRatioTupleList[-1][1] + timeDiff,
                                     fromWavDuration, 1))
        
    # Create the praat script for doing duration manipulation
    durationPointLine = "\tAdd point... %f (1+((%f-1)*zeroedI/(numSteps)))\n"
#     durationPointLine = "\tAdd point... %f %f\n"
    durationPointTextList = []
    for start, end, ratio in interpRatioTupleList:
        durationPointTextList.append(durationPointLine % (start, ratio))
        durationPointTextList.append(durationPointLine % (end, ratio))
    
    durationTierText = "".join(durationPointTextList)
    
    psolaDict = {'num_steps': numSteps,
                 'input_name': fromName,
                 'output_name': fromName,
                 'input_dir': path,
                 'output_dir': outputPath,
                 'pitch_lower_bound': fromMinPitch,
                 'pitch_upper_bound': fromMaxPitch,
                 'durationTierPoints': durationTierText,
                 'start_time': 0,
                 'end_time': fromWavDuration,
                 }
    
    durationScript = common.loadPraatTemplate("psolaDurationPiecewise")
    durationScript %= psolaDict
    
    scriptFNFullPath = join(scriptPath, fromName)
    open(scriptFNFullPath, "w").write(durationScript)
    
    # Run the script
    print "praat %s" % scriptFNFullPath
    common.runPraatScript(praatExe, scriptFNFullPath)
    

def durationMorph(path, fromFN, toFN, numSteps, tierName,
                  plotFlag, fromMinPitch, fromMaxPitch, praatExe):
    '''
    Uses praat to morph duration in one file to duration in another
    
    Praat uses the PSOLA algorithm
    '''
    
    # Prep output directories
    outputPath = join(path, "output")
    utils.makeDir(outputPath)
    
    scriptPath = join(path, "scripts")
    utils.makeDir(scriptPath)
    
    # Constants
    fromName = os.path.splitext(fromFN)[0]
    toName = os.path.splitext(toFN)[0]

    fromWavDuration = audio_scripts.getSoundFileDuration(join(path, fromFN))
    toWavDuration = audio_scripts.getSoundFileDuration(join(path, toFN))
    
    # Get intervals for source and target audio files
    # Use this information to find out how much to stretch/shrink each source
    # interval
    if tierName is None:
        fromTGFN = join(path, fromName + ".TextGrid")
        toTGFN = join(path, toName + ".TextGrid")
        fromExtractInfo = common.getIntervals(fromTGFN, tierName)
        toExtractInfo = common.getIntervals(toTGFN, tierName)
    else:
        fromExtractInfo = [(0, fromWavDuration, ''), ]
        toExtractInfo = [(0, toWavDuration, ''), ]
    
    ratioTupleList = []
    for fromInfoTuple, toInfoTuple in zip(fromExtractInfo, toExtractInfo):
        fromStart, fromEnd = fromInfoTuple[:2]
        toStart, toEnd = toInfoTuple[:2]
        
        # Praat will ignore a second value appearing at the same time as
        # another so we give each start a tiny offset to distinguish intervals
        # that start and end at the same point
        toStart += PRAAT_TIME_DIFF
        fromStart += PRAAT_TIME_DIFF
        
        ratio = (toEnd - toStart) / float((fromEnd - fromStart))

        ratioTuple = (fromStart, fromEnd, ratio)
        ratioTupleList.append(ratioTuple)

    interpRatioTupleList = copy.deepcopy(ratioTupleList)
    # No need to stretch out any pauses at the beginning
    if interpRatioTupleList[0][0] != 0:
        tmpVar = (0, interpRatioTupleList[0][0] - PRAAT_TIME_DIFF, 1)
        interpRatioTupleList.insert(0, tmpVar)

    # Or the end
    if interpRatioTupleList[-1][1] < fromWavDuration:
        interpRatioTupleList.append((interpRatioTupleList[-1][1] +
                                     PRAAT_TIME_DIFF,
                                     fromWavDuration, 1))
        
    # Create the praat script for doing duration manipulation
    durationPointLine = "\tAdd point... %f (1+((%f-1)*zeroedI/(numSteps)))\n"
#     durationPointLine = "\tAdd point... %f %f\n"
    durationPointTextList = []
    for start, end, ratio in interpRatioTupleList:
        durationPointTextList.append(durationPointLine % (start, ratio))
        durationPointTextList.append(durationPointLine % (end, ratio))
    
    durationTierText = "".join(durationPointTextList)
    
    psolaDict = {'num_steps': numSteps,
                 'input_name': fromName,
                 'output_name': "%s_dur_%s" % (fromName, str(tierName)),
                 'input_dir': path,
                 'output_dir': outputPath,
                 'pitch_lower_bound': fromMinPitch,
                 'pitch_upper_bound': fromMaxPitch,
                 'durationTierPoints': durationTierText,
                 'start_time': 0,
                 'end_time': fromWavDuration,
                 }
    
    durationScript = common.loadPraatTemplate("psolaDurationPiecewise")
    durationScript %= psolaDict
    
    scriptFNFullPath = join(scriptPath, fromName)
    open(scriptFNFullPath, "w").write(durationScript)
    
    # Run the script
    print "praat %s" % scriptFNFullPath
    common.runPraatScript(praatExe, scriptFNFullPath)
    
    # Create the adjusted textgrids
    fromTG = praatio.openTextGrid(fromTGFN)
    toTG = praatio.openTextGrid(toTGFN)
    
    fromFN = os.path.split(fromTGFN)[1]
    adjustedTGFN = os.path.splitext(fromFN)[0] + ".TextGrid"
    
    adjustedTG = morphTextgridDuration(fromTG, toTG)
    adjustedTG.save(join(outputPath, adjustedTGFN))
    
    # Plot the results if needed
    if plotFlag:
        
        # Containers
        fromDurList = []
        toDurList = []
        actDurList = []
        labelList = []
        
        # Get durations
        for fromInfoTuple, toInfoTuple in zip(fromExtractInfo, toExtractInfo):
            fromStart, fromEnd = fromInfoTuple[:2]
            toStart, toEnd = toInfoTuple[:2]
            
            labelList.append(fromInfoTuple[2])
            fromDurList.append(fromEnd - fromStart)
            toDurList.append(toEnd - toStart)
            
        # Get iterpolated values
        for i in xrange(numSteps):
            tmpDurList = []
            for fromStart, fromEnd, ratio in ratioTupleList:
                dur = (fromEnd - fromStart)
                multiplier = 1 + (((ratio - 1) * i) / (numSteps - 1))
                tmpDurList.append(dur * multiplier)
            
            actDurList.append(tmpDurList)
        
        # Plot data
        plotFN = "%s_%s.png" % (fromName, tierName)
        plot_morphed_data.plotDuration(fromDurList, toDurList, actDurList,
                                       labelList, join(outputPath, plotFN))


def durationManipulation(path, fromFN, numSteps, tierName,
                         fromMinPitch, fromMaxPitch,
                         modFunc,
                         praatExe,
                         filterFunc=None,
                         outputFolder="output"):
    '''
    Uses praat's PSOLA algorithm to manipulation duration by modFunc amount
    
    modFunc takes as an argument a start and end time and returns the
    new intended start and end time (e.g. + 100 ms or * 10% etc.)
    '''
    
    # By default, all regions are manipulated (except silence)
    if filterFunc is None:
        filterFunc = lambda x: True
    
    # Constants
    fromName = os.path.splitext(fromFN)[0]

    fromWavDuration = audio_scripts.getSoundFileDuration(join(path, fromFN))
    
    # Get intervals for source and target audio files
    # Use this information to find out how much to stretch/shrink each source
    # interval
    if tierName is not None:
        fromTGFN = join(path, fromName + ".TextGrid")
        fromExtractInfo = common.getIntervals(fromTGFN, tierName, filterFunc)
    else:
        fromExtractInfo = [(0, fromWavDuration, ''), ]
    
    ratioTupleList = []
    for fromInfoTuple in fromExtractInfo:
        fromStart, fromEnd = fromInfoTuple[:2]
        toStart, toEnd = modFunc(fromStart, fromEnd)
        
        # Praat will ignore a second value appearing at the same time as
        # another so we give each start a tiny offset to distinguish intervals
        # that start and end at the same point
        toStart += PRAAT_TIME_DIFF
        fromStart += PRAAT_TIME_DIFF
        
        ratio = (toEnd - toStart) / float((fromEnd - fromStart))

        ratioTuple = (fromStart, fromEnd, ratio)
        ratioTupleList.append(ratioTuple)

    if len(ratioTupleList) == 0:
        raise NoLabeledRegionFoundException(fromTGFN)

    _psolaDuration(ratioTupleList, fromWavDuration, PRAAT_TIME_DIFF, path,
                   fromFN, numSteps, tierName, fromMinPitch, fromMaxPitch,
                   outputFolder, praatExe)
    
    # Create the adjusted textgrids
    fromTG = praatio.openTextGrid(fromTGFN)
     
    fromFN = os.path.split(fromTGFN)[1]
    adjustedTGFN = os.path.splitext(fromFN)[0] + ".TextGrid"
      
    adjustedTG = manipulateTextgridDuration(fromTG, modFunc, filterFunc)
    adjustedTG.save(join(join(path, outputFolder), adjustedTGFN))
        

def morphTextgridDuration(fromTG, toTG):
    
    adjustedTG = praatio.Textgrid()
    
    for tierName in fromTG.tierNameList:
        fromTier = fromTG.tierDict[tierName]
        toTier = toTG.tierDict[tierName]
        adjustedTier = fromTier.morph(toTier)
        adjustedTG.addTier(adjustedTier)
            
    return adjustedTG

    
def manipulateTextgridDuration(fromTG, modFunc, filterFunc=None):
    
    # By default, all regions are manipulated (except silence)
    if filterFunc is None:
        filterFunc = lambda x: True
    
    adjustedTG = praatio.Textgrid()
    
    for tierName in fromTG.tierNameList:
        fromTier = fromTG.tierDict[tierName]
        adjustedTier = fromTier.manipulate(modFunc, filterFunc)
        adjustedTG.addTier(adjustedTier)
    
    return adjustedTG
