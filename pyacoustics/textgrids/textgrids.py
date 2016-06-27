'''
Created on Oct 20, 2014

@author: tmahrt
'''

import os
from os.path import join

import codecs

from praatio import tgio

from pyacoustics.utilities import utils


def _navigateTGs(tgPath, name, tierName):
    '''
    Converts a textgrid into a plain text format
    
    Each labels is output by the
    '''
    
    tg = tgio.openTextGrid(join(tgPath, name + ".TextGrid"))
    tier = tg.tierDict[tierName]
    
    for start, stop, label in tier.entryList:
        if label.strip() == "":
            continue
        
        yield start, stop, label


def extractTGInfo(inputPath, outputPath, tierName):
    
    utils.makeDir(outputPath)
    
    for name in utils.findFiles(inputPath, filterExt=".TextGrid",
                                stripExt=True):

        if os.path.exists(join(outputPath, name + ".txt")):
            continue
        print(name)
    
        outputList = []
        for start, stop, label in _navigateTGs(inputPath, name, tierName):
            outputList.append("%f,%f,%s" % (start, stop, label))
            
        outputTxt = "\n".join(outputList)
        outputFN = join(outputPath, name + ".txt")
        with codecs.open(outputFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)


def extractTranscript(featurePath, tierName):
    '''
    Outputs each label of a textgrid on a separate line in a plain text file
    '''
    
    tgPath = join(featurePath, "textgrids")
    
    outputPath = join(featurePath, "transcript")
    utils.makeDir(outputPath)
    
    for name in utils.findFiles(tgPath, filterExt=".TextGrid", stripExt=True):
        
        outputList = []
        for entry in _navigateTGs(tgPath, name, tierName):
            label = entry[2]
            outputList.append("%s" % (label))
        
        outputTxt = "\n".join(outputList)
        outputFN = join(outputPath, name + ".txt")
        with codecs.open(outputFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)


def extractWords(tgPath, tierName, outputPath):
    
    utils.makeDir(outputPath)
    
    for name in utils.findFiles(tgPath, filterExt=".TextGrid", stripExt=True):
        outputList = []
        for entry in _navigateTGs(tgPath, name, tierName):
            label = entry[2]
            for word in label.split():
                outputList.append("%s" % (word))
        
        outputTxt = "\n".join(outputList)
        outputFN = join(outputPath, name + ".txt")
        with codecs.open(outputFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)
