'''
Created on Oct 16, 2012

@author: timmahrt
'''

import math

def _zscoreNormalize(raw, mean, stdDev):
    # No problems related to integers or 64-bit floats (which don't trigger
    # a divide by zero exception)
    raw, mean, stdDev = float(raw), float(mean), float(stdDev)
    return (raw - mean) / stdDev
    

def zscoreNormalizeValue(value, distribution):
    '''
    Appropriate to use when the context (the distribution) varies.
    '''
    mean = sum(distribution) / len(distribution)
    
    tmpList = [(tmpVal - mean) ** 2 for tmpVal in distribution]
    standardDeviation = math.sqrt(sum(tmpList) / len(tmpList))
    
    return _zscoreNormalize(value, mean, standardDeviation)


def syntagmaticNormalization(sampleIndexList, dataList, contextList):
    '''
    Normalizes using local context (before and after the occurrence)
    
    'sampleIndexList' contains the list of indices for values in 'contextList'
        that should be normalized.
    'contextList' provides the indices for all words that should be
        considered (including the present one)
        e.g. for +/- 2 words [-2, -1, 0, 1, 2]
    'featureExtractionFunc' provides the function that extracts the
        relevant feature to be normalized from the words (could be
        a word or syllable level feature)
    '''
    
    dataList = [float(value) for value in dataList]
    
    def doSkipValue(value):
        return value == 0 or value == "None"

    # Get the files associated with this speaker
    #    - be patient, running retrieveStressIndex() takes some time the
    #      first time
#    fnList = fetchFNsForSpeaker(speakerID)

    negativeContextList = [contextI for contextI in contextList
                           if contextI < 0]
    negativeContextList.sort(reverse=True)
    positiveContextList = [contextI for contextI in contextList
                           if contextI > 0]
    positiveContextList.sort()
    
    # Create index
    outputList = []
    for i in sampleIndexList:
        value = dataList[i]
        
        # A value of 0.0 generally is not meaningful
        # (TODO: is there anywhere where this is not the case?)
        if i == -1 or doSkipValue(value):
            outputList.append(0)
            continue
        
        contextValueList = [dataList[i], ]
        
        for (incr, tmpContextList) in [(-1, negativeContextList[:]),
                                       (1, positiveContextList[:])]:
            prevContextValue = dataList[i]
            for contextI in tmpContextList:
                try:
                    assert(i + contextI >= 0)
                    subValue = dataList[i + contextI]
                
                # If we've gone outside the bounds of the file, just
                # repeat the last known good value
                except (IndexError, AssertionError):
                    contextValueList.append(prevContextValue)
                    continue
                
                # Don't count words with meaningless values as part
                # of the context
                if doSkipValue(subValue):
                    tmpContextList.append(tmpContextList[-1] + incr)
                    continue
                
                prevContextValue = subValue
                contextValueList.append(subValue)
                
        normalizedValue = zscoreNormalizeValue(value, contextValueList)
        outputList.append(normalizedValue)
        
    return outputList
