'''
Created on Nov 4, 2014

@author: tmahrt
'''

from pyacoustics.speech_detection import common


def findNextSpeaker(leftFN, rightFN, startTime, analyzeStop, stepSize,
                    numSteps, findLeft=True, leftMin=None, leftMax=None,
                    rightMin=None, rightMax=None):
    '''
    
    '''
    
    audioTuple = common.openAudioFile(leftFN)
    leftAudioFile = audioTuple[0]
    framerate = audioTuple[2]
    rightAudioFile = common.openAudioFile(rightFN)[0]
    
    # Extract the audio frames
    i = 0
    currentSequenceNum = 0
    leftAudioFile.setpos(int(framerate * startTime))
    rightAudioFile.setpos(int(framerate * startTime))
    while currentSequenceNum < numSteps:

        # Stop analyzing once we've reached the end of this interval
        currentTime = startTime + i * stepSize

        if currentTime >= analyzeStop:
            raise common.EndOfAudioData()

        leftRMSEnergy = common.rmsNextFrames(leftAudioFile, stepSize,
                                             leftMin, leftMax)
        rightRMSEnergy = common.rmsNextFrames(rightAudioFile, stepSize,
                                              rightMin, rightMax)
        
        if ((findLeft is True and leftRMSEnergy >= rightRMSEnergy) or
           (findLeft is False and leftRMSEnergy <= rightRMSEnergy)):
            currentSequenceNum += 1
        else:
            currentSequenceNum = 0
        i += 1
    
    endTime = startTime + (i - numSteps) * stepSize
    
    return endTime


def assignAudioEventsForEntries(leftFN, rightFN, leftEntry, rightEntry,
                                stepSize, speakerNumSteps, leftMin, leftMax,
                                rightMin, rightMax):
    '''
    Start up and tear down function for assignAudioEvents()
    '''
    
    # Find the overlap interval and preserve the non-overlapped portions
    start = max(leftEntry[0], rightEntry[0])
    stop = min(leftEntry[1], rightEntry[1])
    
    leftEntryList = common.cropUnusedPortion(leftEntry, start, stop)
    rightEntryList = common.cropUnusedPortion(rightEntry, start, stop)
    
    # Determine who is speaking in overlapped portions
    tmpEntries = assignAudioEvents(leftFN, rightFN, start, stop, stepSize,
                                   speakerNumSteps, leftMin, leftMax, rightMin,
                                   rightMax)
    
    leftEntryList.extend(tmpEntries[0])
    rightEntryList.extend(tmpEntries[1])
    
    # Merge adjacent regions sharing a boundary, if any
    leftEntryList.sort()
    rightEntryList.sort()
    
    leftEntryList = common.mergeAdjacentEntries(leftEntryList)
    rightEntryList = common.mergeAdjacentEntries(rightEntryList)
    
    return leftEntryList, rightEntryList


def assignAudioEvents(leftFN, rightFN, startTime, analyzeStop, stepSize,
                      speakerNumSteps, leftMin, leftMax, rightMin, rightMax):

    findLeft = True
    leftEntryList = []
    rightEntryList = []
    try:
        while True:
            endTime = findNextSpeaker(leftFN, rightFN, startTime, analyzeStop,
                                      stepSize, speakerNumSteps, findLeft,
                                      leftMin, leftMax, rightMin, rightMax)
            
            if endTime > analyzeStop:
                endTime = analyzeStop
            
            if startTime != endTime:
                entry = (startTime, endTime)
                if findLeft:
                    leftEntryList.append(entry)
                else:
                    rightEntryList.append(entry)
            
            print("%f, %f, %f" % (startTime, endTime, analyzeStop))
            startTime = endTime
            findLeft = not findLeft
        
    except common.EndOfAudioData:  # Stop processing
    
        if analyzeStop - startTime > stepSize * speakerNumSteps:
            finalEntry = (startTime, analyzeStop)
            if findLeft:
                leftEntryList.append(finalEntry)
            else:
                rightEntryList.append(finalEntry)
    
    return leftEntryList, rightEntryList


def autosegmentStereoAudio(leftFN, rightFN, leftEntryList, rightEntryList,
                           stepSize, speakerNumSteps):

    overlapThreshold = 0
    overlapCheck = (lambda entry, entryList:
                    [not common.overlapCheck(entry,
                                             cmprEntry,
                                             overlapThreshold)
                     for cmprEntry in entryList]
                    )
    
    # Find the min and max intensity levels for normalizing later
    leftMin, leftMax = common.getMinMaxAmplitude(leftFN,
                                                 stepSize,
                                                 leftEntryList)
    rightMin, rightMax = common.getMinMaxAmplitude(rightFN,
                                                   stepSize,
                                                   rightEntryList)
    
    # First add all of the entries with no overlap
    newLeftEntryList = []
    for leftEntry in leftEntryList:
        
        if all(overlapCheck(leftEntry, rightEntryList)):
            newLeftEntryList.append(leftEntry)
            
    newRightEntryList = []
    for rightEntry in rightEntryList:
        
        if all(overlapCheck(rightEntry, leftEntryList)):
            newRightEntryList.append(rightEntry)
        
    # For all entries with overlap, split them by speaker
    # Utilizing the left channel as a base, this chunks through all overlapping
    # in a single pass of the left channel, until there are no more overlapping
    # segments between the right and left channels.
    i = 0
    while i < len(leftEntryList):
        
        # Check if there are any segments in the right channel that overlap
        # with the current segment in the left channel.  If not, move to
        # the next segment.
        leftEntry = leftEntryList[i]
        overlapCheckList = overlapCheck(leftEntry, rightEntryList)
        if all(overlapCheckList):
            i += 1
            continue
        
        # Otherwise, resolve the first segment in the right channel that
        # overlaps with the current segment
        leftEntry = leftEntryList.pop(i)
        
        j = overlapCheckList.index(False)  # Find the first overlap
        rightEntry = rightEntryList.pop(j)
        
        entryTuple = assignAudioEventsForEntries(leftFN, rightFN, leftEntry,
                                                 rightEntry, stepSize,
                                                 speakerNumSteps, leftMin,
                                                 leftMax, rightMin, rightMax)
        tmpLeftEntryList, tmpRightEntryList = entryTuple
        
        leftEntryList[i:i] = tmpLeftEntryList
        rightEntryList[j:j] = tmpRightEntryList

    # Combine the original non-overlapping segments with the adjusted segments
    newLeftEntryList.extend(leftEntryList)
    newRightEntryList.extend(rightEntryList)
    
    newLeftEntryList.sort()
    newRightEntryList.sort()
    
    newLeftEntryList = [entry for entry in newLeftEntryList
                        if (entry[1] - entry[0] > stepSize * speakerNumSteps)]
    newRightEntryList = [entry for entry in newRightEntryList
                         if (entry[1] - entry[0] > stepSize * speakerNumSteps)]
    
    return newLeftEntryList, newRightEntryList
