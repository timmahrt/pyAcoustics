'''
Created on Oct 11, 2012

@author: timmahrt
'''

import os
from os.path import join

import functools
import itertools
import shutil
import io
import inspect


pyAcousticsPath = os.path.split(inspect.getfile(inspect.currentframe()))[0]
# Get out of the 'utilities' folder
pyAcousticsPath = os.path.split(pyAcousticsPath)[0]
scriptsPath = join(pyAcousticsPath, "praatScripts")


def _getMatchFunc(pattern):
    '''
    An unsophisticated pattern matching function
    '''
    
    # '#' Marks word boundaries, so if there is more than one we need to do
    #    something special to make sure we're not mis-representings them
    assert(pattern.count('#') < 2)

    def startsWith(subStr, fullStr):
        return fullStr[:len(subStr)] == subStr
            
    def endsWith(subStr, fullStr):
        return fullStr[-1 * len(subStr):] == subStr
    
    def inStr(subStr, fullStr):
        return subStr in fullStr

    # Selection of the correct function
    if pattern[0] == '#':
        pattern = pattern[1:]
        cmpFunc = startsWith
        
    elif pattern[-1] == '#':
        pattern = pattern[:-1]
        cmpFunc = endsWith
        
    else:
        cmpFunc = inStr
    
    return functools.partial(cmpFunc, pattern)


def findFiles(path, filterPaths=False, filterExt=None, filterPattern=None,
              skipIfNameInList=None, stripExt=False):
    
    fnList = os.listdir(path)
       
    if filterPaths is True:
        fnList = [folderName for folderName in fnList
                  if os.path.isdir(os.path.join(path, folderName))]

    if filterExt is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        fnList = [fn for fn, name, ext in splitFNList if ext == filterExt]
        
    if filterPattern is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        matchFunc = _getMatchFunc(filterPattern)
        fnList = [fn for fn, name, ext in splitFNList if matchFunc(name)]
    
    if skipIfNameInList is not None:
        targetNameList = [os.path.splitext(fn)[0] for fn in skipIfNameInList]
        fnList = [fn for fn in fnList
                  if os.path.splitext(fn)[0] not in targetNameList]
    
    if stripExt is True:
        fnList = [os.path.splitext(fn)[0] for fn in fnList]
    
    fnList.sort()
    return fnList
    

def openCSV(path, fn, valueIndex=None, encoding="utf-8"):
    '''
    Load a feature
    
    In many cases we only want a single value from the feature (mainly because
    the feature only contains one value).  In these situations, the user
    can indicate that rather than receiving a list of lists, they can receive
    a lists of values, where each value represents the item in the row
    indicated by valueIndex.
    '''
    
    # Load CSV file
    with io.open(join(path, fn), "r", encoding=encoding) as fd:
        featureList = fd.read().splitlines()
    featureList = [row.split(",") for row in featureList]
    
    if valueIndex is not None:
        featureList = [row[valueIndex] for row in featureList]
    
    return featureList


def changeFileType(path, fromExt, toExt):
    
    if fromExt[0] != ".":
        fromExt = "." + fromExt
    if toExt[0] != ".":
        toExt = "." + toExt
        
    for fn in os.listdir(path):
        name, ext = os.path.splitext(fn)
        if ext == fromExt:
            shutil.move(join(path, fn), join(path, name + toExt))


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def extractLines(path, matchStr, outputDir="output"):
    
    outputPath = join(path, outputDir)
    makeDir(outputPath)
    
    for fn in findFiles(path, filterExt=".csv"):
        with io.open(join(path, fn), "r", encoding='utf-8') as fd:
            data = fd.read()
        dataList = data.split("\n")
        
        dataList = [line for line in dataList if matchStr in line]
        
        with io.open(join(outputPath, fn), "w", encoding='utf-8') as fd:
            fd.write("\n".join(dataList))


def cat(fn1, fn2, outputFN):
    with io.open(fn1, 'r', encoding='utf-8') as fd:
        txt1 = fd.read()
    with io.open(fn2, 'r', encoding='utf-8') as fd:
        txt2 = fd.read()
    
    with io.open(outputFN, 'w', encoding='utf-8') as fd:
        fd.write(txt1 + txt2)


def catAll(path, ext, ensureNewline=False):
    outputPath = join(path, "cat_output")
    makeDir(outputPath)

    outputList = []
    for fn in findFiles(path, filterExt=ext):
        with io.open(join(path, fn), "r", encoding='utf-8') as fd:
            data = fd.read()

        if ensureNewline and data[-1] != "\n":
            data += "\n"

        outputList.append(data)

    outputTxt = "".join(outputList)
    outputFN = join(outputPath, "catFiles" + ext)
    with io.open(outputFN, "w", encoding='utf-8') as fd:
        fd.write(outputTxt)


def whatever(path):
    outputList = []
    for fn in findFiles(path, filterExt=".txt"):
        outputList.extend([fn, ] * 30)

    for fn in outputList:
        print(fn)


def divide(numerator, denominator, zeroValue):
    if denominator == 0:
        retValue = zeroValue
    else:
        retValue = numerator / float(denominator)

    return retValue


def safeZip(listOfLists, enforceLength):

    if enforceLength is True:
        length = len(listOfLists[0])
        assert(all([length == len(subList) for subList in listOfLists]))

    return itertools.izip_longest(*listOfLists)
