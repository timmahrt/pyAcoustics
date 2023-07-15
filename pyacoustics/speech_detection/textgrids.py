"""
Created on Nov 5, 2014

@author: tmahrt

Textgrid utilities for saving the output of speech detection code into
praat textgrids.
"""

from praatio import textgrid


def outputTextgrid(outputFN, duration, entryList, tierName):

    # Give all entries a label indicating their order of occurrence
    entryList.sort()
    newEntryList = [(entry[0], entry[1], str(i)) for i, entry in enumerate(entryList)]

    # Output textgrid
    tierSpeech = textgrid.IntervalTier(tierName, newEntryList, 0, duration)

    tg = textgrid.Textgrid()
    tg.addTier(tierSpeech)
    tg.save(outputFN, format="short_textgrid", includeBlankSpaces=True)


def outputStereoTextgrid(
    outputFN, duration, leftEntryList, rightEntryList, leftChannelName, rightChannelName
):

    # Give all entries a label indicating their order of occurrence
    leftEntryList.sort()
    newLeftEntryList = [
        (entry[0], entry[1], str(i)) for i, entry in enumerate(leftEntryList)
    ]

    rightEntryList.sort()
    newRightEntryList = [
        (entry[0], entry[1], str(i)) for i, entry in enumerate(rightEntryList)
    ]

    # This shouldn't be necessary
    newLeftEntryList = [
        entry
        for entry in newLeftEntryList
        if entry[1] <= duration and entry[0] < entry[1]
    ]
    newRightEntryList = [
        entry
        for entry in newRightEntryList
        if entry[1] <= duration and entry[0] < entry[1]
    ]

    # Output textgrid
    leftTier = textgrid.IntervalTier(leftChannelName, newLeftEntryList, 0, duration)
    rightTier = textgrid.IntervalTier(rightChannelName, newRightEntryList, 0, duration)

    outputTG = textgrid.Textgrid()
    outputTG.addTier(leftTier)
    outputTG.addTier(rightTier)

    outputTG.save(outputFN, format="short_textgrid", includeBlankSpaces=True)
