'''
Created on Jun 5, 2013

@author: timmahrt
'''
import math

from pyacoustics.utilities import my_math


DO_SAMPLE_GATED = 1  # Each subsequence overlaps by (n-1)/2
DO_SAMPLE_EXCLUSIVE = 2  # No index appears in two subsequences
DO_SAMPLE_ALL = 3  # Each index acts as the control point once


def compressList(targetList):
    '''
    Compresses a list into pairs of the form (value, num_continuous_occurances)
    
    e.g. targetList = [1, 1, 1, 1, 2, 2, 1, 1, 3]
    >> [(1,4), (2, 2), (1, 2), (3, 1),]
    '''
    
    currentValue = targetList[0]
    startIndex = 0
    i = 0
    
    outputList = []
    while i < len(targetList):
        if targetList[i] == currentValue:
            i += 1
            continue
        
        outputList.append([currentValue, startIndex, i])
        
        currentValue = targetList[i]
        startIndex = i
        i += 1
    
    if len(outputList) == 0 or outputList[-1][0] != currentValue:
        outputList.append([currentValue, startIndex, i])
        
    return outputList


def compressedListTransform(compressedList, timeStep, timeThreshold=None):
    '''
    Isolates the unique values in compressedList and converts them to time
    
    timeThreshold can be set to ignore values that are not long enough, adding
    their content to whatever came before (prevents fragmenting data too much).
    '''
    
    returnDict = {}
    countDict = {}
    lastGoodLabel = None
    for label, start, end in compressedList:
     
        countDict.setdefault(label, 0)
        returnDict.setdefault(label, [])
     
        startTime = start * timeStep
        endTime = end * timeStep
        
        # Merge this entry with the previous one
        # if it is too short (noise tolerance)
        tmpDuration = (end - start) * timeStep
        if timeThreshold is not None and tmpDuration < timeThreshold:
            
            # If the very first entry is less than 0.3 seconds long
            if lastGoodLabel is not None and returnDict[lastGoodLabel] != []:
                returnDict[lastGoodLabel][-1][1] = endTime
                continue
        
        # If the previous label and this one are the same, merge entries
        if label == lastGoodLabel:
            returnDict[label][-1][1] = endTime
            
        # Otherwise, create a new entry
        else:
            returnDict[label].append([startTime, endTime,
                                      str(countDict[label])])
            countDict[label] += 1
            lastGoodLabel = label
                
    return returnDict


def sampleMiddle(dataList, i, chunkSize):
    '''
    The control point lies in the center (i - 1 ) / 2.0
    '''
    assert((chunkSize % 2) == 1)  # i must be an odd number
    halfChunk = int(math.floor(chunkSize / 2.0))
    
    subList = []
    indexList = []
    start = i - halfChunk if i - halfChunk >= 0 else 0
    end = i + halfChunk if i + halfChunk < len(dataList) else len(dataList) - 1
    
    # Handling underflow
    if i - halfChunk < 0:
        subList += [dataList[0], ] * abs(i - halfChunk)
        indexList += [0, ] * abs(i - halfChunk)
    
    # The normal range
    mainBody = [dataList[j] for j in range(start, end + 1)]
    uniqueChunkLen = len(mainBody)
    subList.extend(mainBody)
    indexList.extend([j for j in range(start, end + 1)])
    
    # Handling overflow
    if i + halfChunk >= len(dataList):
        subList += [dataList[len(dataList) - 1], ] * ((1 + i + halfChunk) -
                                                      len(dataList))
        indexList.extend([len(dataList) - 1, ] * ((1 + i + halfChunk -
                                                   len(dataList))))

    return subList, indexList, uniqueChunkLen


def sampleLeft(dataList, i, chunkSize):
    '''
    The control point lies on the left edge (i = 0)
    '''
    subList = []
    indexList = []
    start = i
    end = i + chunkSize if i + chunkSize < len(dataList) else len(dataList)
    
    # The normal range
    mainBody = [dataList[j] for j in range(start, end)]
    uniqueChunkLen = len(mainBody)
    subList.extend(mainBody)
    indexList.extend([j for j in range(start, end)])
    
    # Handling overflow
    if i + chunkSize >= len(dataList):
        subList += [dataList[len(dataList) - 1], ] * ((1 + i + chunkSize) -
                                                      len(dataList))
        indexList += [len(dataList) - 1, ] * ((1 + i + chunkSize) -
                                              len(dataList))
        
    return subList, indexList, uniqueChunkLen


def sampleRight(dataList, i, chunkSize):
    '''
    The control point lies on the right edge (i = -1)
    '''
    subList = []
    indexList = []
    start = 1 + i - chunkSize if 1 + i - chunkSize >= 0 else 0
    end = i + 1 if i < len(dataList) else len(dataList)
    
    # Handling underflow
#     print("blah", abs(i - chunkSize), start, end)
    if i - chunkSize < 0:
        subList += [dataList[0], ] * (abs(i - chunkSize + 1))
        indexList += [0, ] * (abs(i - chunkSize + 1))
    
    # The normal range
#     print(start, end)
    mainBody = [dataList[j] for j in range(start, end)]
    uniqueChunkLen = len(mainBody)
    subList.extend(mainBody)
    indexList.extend([j for j in range(start, end)])
    
    # Handling overflow
    if i >= len(dataList):
        subList += [dataList[len(dataList) - 1], ] * (chunkSize -
                                                      len(indexList))
        indexList += [len(dataList) - 1, ] * (chunkSize - len(indexList))
    
    return subList, indexList, uniqueChunkLen


def subsequenceGenerator(dataList, chunkSize, sampleFunc, stepSizeFlag):
    '''
    Can iteratively generate subsequences in a variety of fashions
    
    chunkSize - the size of each chunk
    sampleFunc - e.g. sampleMiddle(), sampleLeft(), sampleRight(), determines
        the 'controlPoint'
    stepSize - the distance between starting points
    
    Regardless of the parameters, all values will appear in one of the
    subsequences, including the endpoints.  Each subsequence is the same
    length--if necessary, values are repeated on the tail ends of the
    list
    '''
    
    if stepSizeFlag == DO_SAMPLE_EXCLUSIVE:
        stepSize = chunkSize
    elif stepSizeFlag == DO_SAMPLE_GATED:
        stepSize = int(math.floor(chunkSize / 2.0))
    elif stepSizeFlag == DO_SAMPLE_ALL:
        stepSize = 1
    
    controlPoint = 0
    finalIndex = 0
    doneIterating = False
    while not doneIterating:
        
        subSequence, subSequenceIndices, sampledLen = sampleFunc(dataList,
                                                                 controlPoint,
                                                                 chunkSize)
        
        finalIndex = subSequenceIndices[-1]
        isEndpointLastValue = finalIndex >= (len(dataList) - 1)
        isControlPointLastValue = controlPoint >= (len(dataList) - 1)
        
        # Regardless of what the control point was, end when the last index
        # in the subset matches the length of the data list
        if stepSizeFlag == DO_SAMPLE_EXCLUSIVE:
            doneIterating = isEndpointLastValue
        
        # When the control point index reaches the end of the data list
        # (i.e., all values have been represented in some list, end)
        else:
            doneIterating = isControlPointLastValue

        controlPoint += stepSize

        if stepSizeFlag == DO_SAMPLE_GATED:
            
            if sampleFunc == sampleMiddle:
                region = subSequenceIndices[int((chunkSize - 1) / 2.0):-1]
            elif sampleFunc == sampleLeft:
                region = subSequenceIndices[:int((chunkSize - 1) / 2.0)]
            elif sampleFunc == sampleRight:
                region = subSequenceIndices[int((chunkSize - 1) / 2.0) + 1:]
            
            sampledLen = int((chunkSize - 1) / 2.0)
            sampledLen = sampledLen - (sampledLen - len(set(region)))
        
            if doneIterating and sampleFunc != sampleRight:
                sampledLen = 0
        
        yield subSequence, subSequenceIndices, sampledLen
    
    
def interp(start, stop, n):
    for i in range(n):
        yield start + i * (stop - start) / float(n - 1)


# Adapted this from online - for getting a set of evenly spaced intervals
# from a list
# http://stackoverflow.com/questions/10084436/generating-evenly-distributed-
# multiples-samples-within-a-range
def getEvenlySpacedSteps(start, end, n):
    
    assert (end + 1 - start >= n)
    
    # The usual case
    if n != 1:
        step = (end - start) / float(n - 1)
        retList = [int(round(start + x * step)) for x in range(n)]
        
    # If someone only wants 1 sample, just take the middle sample
    elif n == 1:
        step = (end - start) / float(2)
        retList = [int(round((end - start) / float(2))), ]
    
    return retList


def binDistribution(distList, numBins, minV=None, maxV=None):
    '''
    Places all data into the closest of n evenly spaced bins
    '''
    
    if minV is None:
        minV = min(distList)
    
    if maxV is None:
        maxV = max(distList)
        
    binValueArray = my_math.linspace(minV, maxV, numBins)
    
    binnedValueList = []
    for value in distList:
        diffList = list(abs(binValueArray - value))
        smallestDiff = min(diffList)
        binIndex = diffList.index(smallestDiff)
        
        binnedValueList.append(binValueArray[binIndex])
    
    return binnedValueList


def findLongestSublist(listOfLists):
    longestList = []
    i = None
    for i, lst in enumerate(listOfLists):
        if len(lst) > len(longestList):
            longestList = lst

    return i, longestList


def invertIntervalList(entryList, minValue=0, maxValue=None):
    '''
    Given a list of ordinal events, inverts the start and end positions
    
    e.g. input [(5, 6), (10, 13), (14, 16)]
         output [(0, 5), (6, 10), (13, 14)]
    '''
    newEntryList = []
    i = 0
    
    # Add possible initial interval
    if minValue is not None:
        if entryList[0][0] > minValue:
            newEntryList.append((minValue, entryList[0][0]))
    
    while i + 1 < len(entryList):
        newEntryList.append((entryList[i][1], entryList[i + 1][0]))
        i += 1
        
    # Add possible trailing interval
    if maxValue is not None:
        if entryList[i][1] < maxValue:
            newEntryList.append((entryList[i][1], maxValue))
            
    return newEntryList
