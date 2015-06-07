'''
Created on Sep 18, 2013

@author: timmahrt

Given two lists of tuples of the form [(value, time), (value, time)], morph
can iteratively transform the values in one list to the values in the other
while maintaining the times in the first list.

Both time scales are placed on a relative scale.  This assumes that the times
may be different and the number of samples may be different but the 'events'
occur at the same relative location (half way through, at the end, etc.).

Both dynamic time warping and morph, align two data lists in time.  However,
dynamic time warping does this by analyzing the event structure and aligning
events in the two signals as best it can
(i.e. it changes when events happen in relative time while morph preserves
when events happen in relative time).
'''


class RelativizeSequenceException(Exception):
    
    def __init__(self, dist):
        super(RelativizeSequenceException, self).__init__()
        self.dist = dist
        
    def __str__(self):
        return "You need at least two unique values to make " + \
            "a sequence relative. Input: %s" % repr(self.dist)

    
def makeSequenceRelative(absVSequence):
    '''
    Puts every value in a list on a continuum between 0 and 1
    
    Also returns the min and max values (to reverse the process)
    '''
    
    if len(absVSequence) < 2 or len(set(absVSequence)) == 1:
        raise RelativizeSequenceException(absVSequence)
    
    minV = min(absVSequence)
    maxV = max(absVSequence)
    relativeSeq = [(value - minV) / (maxV - minV) for value in absVSequence]
    
    return relativeSeq, minV, maxV


def makeSequenceAbsolute(relVSequence, minV, maxV):
    '''
    Makes every value in a sequence absolute
    '''

    return [(value * (maxV - minV)) + minV for value in relVSequence]


def _makeTimingRelative(absoluteDataList):
    '''
    Given normal pitch tier data, puts the times on a scale from 0 to 1
    
    Input is a list of tuples of the form
    ([(time1, pitch1), (time2, pitch2),...]
    
    Also returns the start and end time so that the process can be reversed
    '''
    
    valueSeq = [value for value, _ in absoluteDataList]
    timingSeq = [time for _, time in absoluteDataList]
    
    relTimingSeq, startTime, endTime = makeSequenceRelative(timingSeq)
    
    relDataList = [(value, time) for value, time
                   in zip(valueSeq, relTimingSeq)]
    
    return relDataList, startTime, endTime


def _makeTimingAbsolute(relativeDataList, startTime, endTime):
    '''
    Maps values from 0 to 1 to the provided start and end time
    
    Input is a list of tuples of the form
    ([(time1, pitch1), (time2, pitch2),...]
    '''

    valueSeq = [value for value, _ in relativeDataList]
    timingSeq = [time for _, time in relativeDataList]

    absTimingSeq = makeSequenceAbsolute(timingSeq, startTime, endTime)
    
    absDataList = [(value, time) for value, time
                   in zip(valueSeq, absTimingSeq)]
    
    return absDataList
    
    
def _alignDataPoints(fromList, toList):
    '''
    Finds the indicies for data points that are closest to each other in time.
    
    The inputs should be in relative time, scaled from 0 to 1
    '''
    
    fromTimeList = [dataTuple[1] for dataTuple in fromList]
    toTimeList = [dataTuple[1] for dataTuple in toList]
        
    indexList = []
    for fromTimestamp in fromTimeList:
        timeDiffList = [abs(toTimestamp - fromTimestamp)
                        for toTimestamp in toTimeList]
        smallestDiff = min(timeDiffList)
        i = timeDiffList.index(smallestDiff)
        indexList.append(i)
    
    return indexList


def morphDataLists(fromList, toList, numSteps):
    '''
    Iteratively morph fromList into toList in numSteps steps
    '''
    
    # If there are more than 1 pitch value, then we align the data in
    # relative time.
    # Each data point comes with a timestamp.  The earliest timestamp is 0
    # and the latest timestamp is 1.  Using this method, for each relative
    # timestamp in the source list, we find the closest relative timestamp
    # in the target list.  Just because two pitch values have the same index
    # in the source and target lists does not mean that they correspond to
    # the same speech event.
    fromListRel, fromStartTime, fromEndTime = _makeTimingRelative(fromList)
    toListRel = _makeTimingRelative(toList)[0]
    
    # If fromList has more points, we'll have flat areas
    # If toList has more points, we'll might miss peaks or valleys
    indexList = _alignDataPoints(fromListRel, toListRel)
    alignedToPitchRel = [toListRel[i] for i in indexList]
    
    for i in xrange(numSteps):
        newPitchList = []
        
        # Perform the interpolation
        for fromTuple, toTuple in zip(fromListRel, alignedToPitchRel):
            fromValue, fromTime = fromTuple
            toValue, toTime = toTuple
            
            if numSteps > 1:
                iterVal = i / float(numSteps - 1)
                newValue = fromValue + (iterVal * (toValue - fromValue))
                newTime = fromTime + (iterVal * (toTime - fromTime))
            else:
                newValue = toValue
                newTime = toTime
            
            newPitchList.append((newValue, newTime))
        
        newPitchList = _makeTimingAbsolute(newPitchList, fromStartTime,
                                           fromEndTime)
        
        yield i, newPitchList


def morphChunkedDataLists(fromDataList, toDataList, numSteps):
    '''
    Morph one set of data into another, in a stepwise fashion
    
    A convenience function.  Given a set of paired data lists,
    this will morph each one individually.
    
    Returns a single list with all data combined together.
    '''
    
    assert(len(fromDataList) == len(toDataList))
    
    # Morph the fromDataList into the toDataList
    outputList = []
    for x, y in zip(fromDataList, toDataList):
        
        # We cannot morph a region if there is no data or only
        # a single data point for either side
        if (len(x) < 2) or (len(y) < 2):
            continue
        
        tmpList = [outputPitchList for i, outputPitchList
                   in morphDataLists(x, y, numSteps)]
        outputList.append(tmpList)
        
    # Transpose list
    finalOutputList = outputList.pop(0)
    for subList in outputList:
        for i, subsubList in enumerate(subList):
            finalOutputList[i].extend(subsubList)

    return finalOutputList
