'''
Created on Apr 2, 2015

@author: tmahrt
'''

import os
from os.path import join

import math
import copy

from pyacoustics.morph.morph_utils import common
from pyacoustics.morph.morph_utils import plot_morphed_data
from pyacoustics.utilities import utils
from pyacoustics.utilities import sequences
from pyacoustics.signals import audio_scripts
from pyacoustics.utilities import my_math


def intensityMorph(fromWavFN, toWavFN, fromWavTGFN, toWavTGFN, tierName,
                   numSteps, coreChunkSize, plotFlag):
    
    fromDataTupleList = common.getIntervals(fromWavTGFN, tierName)
    toDataTupleList = common.getIntervals(toWavTGFN, tierName)
    
    outputName = os.path.splitext(fromWavFN)[0] + "_int_" + tierName
    
    _intensityMorph(fromWavFN, toWavFN,
                    fromDataTupleList, toDataTupleList,
                    numSteps, coreChunkSize, plotFlag, outputName)

    
def _intensityMorph(fromWavFN, toWavFN, fromDataTupleList,
                    toDataTupleList, numSteps, coreChunkSize, plotFlag,
                    outputName=None):
    
    if outputName is None:
        outputName = os.path.splitext(fromWavFN)[0] + "_int"
    
    outputDir = join(os.path.split(fromWavFN)[0], "output")
    utils.makeDir(outputDir)
    
    # Determine the multiplication values to be used in normalization
    # - this extracts one value per chunk
    expectedLength = 0
    normFactorList = []
    truncatedToList = []
    chunkSizeList = []
    fromDataList = []
    
    fromParams = audio_scripts.getParams(fromWavFN)
    toParams = audio_scripts.getParams(toWavFN)
    
    for fromTuple, toTuple in zip(fromDataTupleList, toDataTupleList):
        
        fromStart, fromEnd = fromTuple[:2]
        toStart, toEnd = toTuple[:2]
        
        expectedLength += (fromEnd - fromStart) * fromParams[2]
        
        fromDataList.extend(fromSubWav.rawDataList)
        
        normFactorListTmp, a = getRelativeNormalizedFactors(fromSubWav,
                                                            toSubWav,
                                                            coreChunkSize)
        tmpChunkList = [tmpChunkSize
                        for value, tmpChunkSize in normFactorListTmp]
        chunkSizeList.append(sum(tmpChunkList))
        normFactorList.extend(normFactorListTmp)
        truncatedToList.extend(a)
 
    interpolatedResults = []
    normFactorGen = [sequences.interp(1.0, factor[0], numSteps)
                     for factor in normFactorList]
    tmpChunkSizeList = [factor[1] for factor in normFactorList]
    for i in xrange(numSteps):

        outputFN = "%s_s%d_%d_%d.wav" % (outputName,
                                         coreChunkSize,
                                         numSteps - 1, i)
 
        tmpNormFactorList = [next(normFactorGen[j])
                             for j in xrange(len(normFactorGen))]
        
        # Skip the first value (same as the input value)
        if i == 0:
            continue
        
        tmpInputList = zip(tmpNormFactorList, tmpChunkSizeList)
        
        normalizationTuple = expandNormalizationFactors(tmpInputList)
        expandedNormFactorList = normalizationTuple[0]

        # It happened once that the expanded factor list was off by one value
        # -- I could not determine why, so this is just a cheap hack
        if len(expandedNormFactorList) == (expectedLength - 1):
            expandedNormFactorList.append(expandedNormFactorList[-1])

#         print("Diff: ", expectedLength, len(expandedNormFactorList))
        assert(expectedLength == len(expandedNormFactorList))
        
        newWavObj = copy.deepcopy(fromWavObj)
        newRawDataList = []
    
        # Apply the normalization and reinsert the data back
        # into the original file
        offset = 0
        for fromTuple, chunkSize in zip(fromDataTupleList, chunkSizeList):
            fromStart, fromEnd = fromTuple[:2]
            fromSubWav = fromWavObj.extractSubsegment(fromStart, fromEnd)
            assert(len(fromSubWav.rawDataList) ==
                   len(expandedNormFactorList[offset:offset + chunkSize]))
            
            tmpList = [fromSubWav.rawDataList,
                       expandedNormFactorList[offset:offset + chunkSize]]
            subRawDataList = [value * normFactor for value, normFactor in
                              utils.safeZip(tmpList, enforceLength=True)]
            newRawDataList.extend(subRawDataList)
            
            offset += chunkSize
        
        newWavObj = audio.WavObj(newRawDataList, fromWavObj.samplingRate)
        newWavObj.save(join(outputDir, outputFN))
        
        interpolatedResults.append(newWavObj.rawDataList)
        
    plotFN = "%s_s%d_%d.png" % (outputFN, coreChunkSize, numSteps)
    
    if plotFlag:
        plotMorphedData.plotIntensity(fromDataList,
                                      truncatedToList,
                                      interpolatedResults,
                                      expandedNormFactorList,
                                      os.path.join(outputDir, plotFN))


def getNormalizationFactor(lst, refLst=None):
    '''
    
    '''
    
    # Get the source values that we will be normalizing
    lst = list(set(lst))
    if 0 in lst:
        lst.pop(lst.index(0))

    actMaxV = float(max(lst))
    actMinV = float(min(lst))
    
    # Get the reference values
    if refLst is None:
        refMaxV = 32767.0
        refMinV = -32767.0
    else:
        refLst = list(set(refLst))
        if 0 in refLst:
            refLst.pop(refLst.index(0))
         
        refMaxV = float(max(refLst))
        refMinV = float(min(refLst))
    
    actualFactor = min(refMaxV / actMaxV, abs(refMinV) / abs(actMinV))
#     print("Normalization factor: ", actualFactor)
    
    return actualFactor


def getRelativeNormalizedFactors(fromDataList, toDataList, chunkSize):
    '''
    Determines the factors to be used to normalize sourceWav from  targetWav
    
    This can be used to relatively normalize the source based on the target
    on an iterative basis (small chunks are normalized rather than the entire
    wav.
    '''
    
    # Sample proportionately from the targetWav
    # - if the two lists are the same length, there is no change
    # - if /target/ is shorter, it will be lengthened with some repeated values
    # - if /target/ is longer, it will be shortened with some values dropped
    tmpIndexList = sequences.interp(0, len(toDataList) - 1,
                                    fromDataList)
    newTargetRawDataList = [toDataList[int(round(i))]
                            for i in tmpIndexList]
    
    assert(len(fromDataList) == len(newTargetRawDataList))
    
    fromGen = sequences.subsequenceGenerator(fromDataList,
                                             chunkSize,
                                             sequences.sampleMiddle,
                                             sequences.DO_SAMPLE_GATED)
    toGen = sequences.subsequenceGenerator(newTargetRawDataList,
                                           chunkSize,
                                           sequences.sampleMiddle,
                                           sequences.DO_SAMPLE_GATED)
    
    normFactorList = []
    i = 0
    for fromTuple, toTuple in zip(fromGen, toGen):
        fromDataChunk = fromTuple[0]
        toDataChunk = toTuple[0]
        distToNextControlPoint = fromTuple[2]
        normFactor = getNormalizationFactor(fromDataChunk, toDataChunk)
        normFactorList.append((normFactor, distToNextControlPoint))
#         i += 1
#         if i >= 38:
#             print("hello")
    
#     print(len(sourceWav.rawDataList), allChunks)
#     assert(len(sourceWav.rawDataList) == allChunks)
    return normFactorList, newTargetRawDataList


def expandNormalizationFactors(normFactorList):
    '''
    Expands the normFactorList from being chunk-based to sample-based
    
    E.g. A wav with 1000 samples may be represented by a factorList of 5 chunks
    (5 factor values).  This function will expand that to 1000.
    '''
    
    i = 0
    normFactorsFull = []
    controlPoints = []
    while i < len(normFactorList) - 1:
        startVal, chunkSize = normFactorList[i]
        endVal = normFactorList[i + 1][0]
        normFactorsFull.extend(my_math.linspace(startVal, endVal, chunkSize))
        
        controlPoints.append(startVal)
        controlPoints.extend(my_math.linspace(startVal, startVal,
                                              chunkSize - 1))
        i += 1
    
    # We have no more data, so just repeat the final norm factor at the tail
    # of the file
    value, finalChunkSize = normFactorList[i]
    controlPoints.append(value)
    controlPoints.extend(my_math.linspace(startVal, startVal,
                                          finalChunkSize - 1))
    normFactorsFull.extend(my_math.linspace(value, value, finalChunkSize))
    
    print('Norm factors full: %d' % len(normFactorsFull))
    return normFactorsFull, controlPoints
