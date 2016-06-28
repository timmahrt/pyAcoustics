# -*- coding: utf-8 -*-

from os.path import join
from itertools import izip, islice
import math
import io

from pyacoustics.utilities import utils


class CountCorpus(object):
    
    def __init__(self, frequencyDict, totalCount=None):
        '''
        A generic class for handling corpora.
        
        For large corpora you can save the totalCount somewhere and pass it
        in during instantiation.  Otherwise, it will be calculated at
        runtime.
        '''
        self.frequencyDict = frequencyDict
        
        if totalCount is None:
            totalCount = self._getNumWords()
        self.totalCount = totalCount
    
    def getFrequency(self, word, normFunc=None, outOfDictionaryValue=None):
        try:
            count = self.frequencyDict[word]
        except KeyError:
            if outOfDictionaryValue is None:
                raise
            else:
                print("OOD Word: %s" % word)
                count = outOfDictionaryValue
        
        if normFunc is None:
            freq = float(count) / self.totalCount
        else:
            freq = normFunc(count, self.totalCount)
            
        logFreq = math.log(freq)
        
        return count, freq, logFreq
        
    def _getNumWords(self):
        '''
        Gets the number of words in the corpus
        '''
        sumV = 0
        for word in self.frequencyDict.keys():
            sumV += self.frequencyDict[word]
            
        return sumV
    

class GoogleUnigram(CountCorpus):
    
    NUM_WORDS = 1024908267229.0
    
    def __init__(self, googleUnigram):
        
        # Load the corpus data
        frequencyDict = {}
        with open(googleUnigram, "r") as fd:
            data = fd.read()
        dataList = data.split()
        for (word, count) in izip(islice(dataList, 0, None, 2),
                                  islice(dataList, 1, None, 2)):
            frequencyDict[word] = count
            
        super(GoogleUnigram, self).__init__(frequencyDict,
                                            GoogleUnigram.NUM_WORDS)


class Switchboard(CountCorpus):
    
    NUM_WORDS = 1456224.0
    
    def __init__(self, switchboardCounts):
        
        # Load the corpus
        frequencyDict = {}
        with open(switchboardCounts, "r") as fd:
            data = fd.read()
        
        dataList = data.split("\n")
        dataList = [row[1:-2].strip() for row in dataList
                    if len(row) > 2 and row[0] != ";"]
        dataList = [row.split(" ") for row in dataList]
        
        for row in dataList:
            word = row[0]
            count = row[-4]
            frequencyDict[word] = int(count)
        
        super(Switchboard, self).__init__(frequencyDict, Switchboard.NUM_WORDS)

    
class SwitchboardTim(CountCorpus):
    
    NUM_WORDS = 1464017.0
    
    def __init__(self, switchboardCounts):
        frequencyDict = loadCountList(switchboardCounts)
        super(SwitchboardTim, self).__init__(frequencyDict,
                                             SwitchboardTim.NUM_WORDS)
        
        
class Buckeye(CountCorpus):
    
    NUM_WORDS = 35009.0
    
    def __init__(self, buckeyeCounts):
        frequencyDict = loadCountList(buckeyeCounts)
        super(Buckeye, self).__init__(frequencyDict, Buckeye.NUM_WORDS)


class Fischer(CountCorpus):

    NUM_WORDS = 21025946.0

    def __init__(self, fischerCounts):
        frequencyDict = loadCountList(fischerCounts)
        super(Fischer, self).__init__(frequencyDict, Fischer.NUM_WORDS)
        
        
class Crea(CountCorpus):
    
    NUM_WORDS = 152554665
    
    def __init__(self, creaCounts):
        frequencyDict = loadCountList(creaCounts)
        super(Crea, self).__init__(frequencyDict, Crea.NUM_WORDS)
    

class FrenchCorpus(CountCorpus):
    
    NUM_WORDS = None
    
    def __init__(self, frenchCounts):
        frequencyDict = loadCountList(frenchCounts)
        super(FrenchCorpus, self).__init__(frequencyDict, 0)


def calcWordsPerMillion(count, totalCount):
    million = 1000000
    assert(totalCount > million)
    return count * million / totalCount


def loadFrenchList(fnFullPath, outputFullPath):
    
    with io.open(fnFullPath, "r", encoding="utf-8") as fd:
        data = fd.read()
    frequencyDict = {}
    
    dataList = data.splitlines()
    dataList = [row.rsplit(",") for row in dataList[1:]]
    dataList = [(rowList[0], float(rowList[6])) for rowList in dataList]
    
    # Some items appear multiple times but with different meanings
    countList = [dataList.pop(0)]
    for word, count in dataList:
        if word == countList[-1][0]:
            countList[-1] = (word, countList[-1][1] + count)
        else:
            countList.append((word, count))
    
    countList = [",".join((word, str(count))) for word, count in countList]
    
    with io.open(outputFullPath, "w", encoding="utf-8") as fd:
        fd.write("\n".join(countList))


def loadCountList(fnFullPath):
    '''
    Loads counts from file that stores word counts in the form "word, count\n"
    '''
    with io.open(fnFullPath, "r", encoding="utf-8") as fd:
        data = fd.read()
    frequencyDict = {}
    
    dataList = data.split("\n")
    dataList = [row.rsplit(",", 1) for row in dataList]
    
    for word, count in dataList:
        frequencyDict[word] = float(count)
    
    return frequencyDict


def findFrequenciesForWordLists(featurePath, countObj, frequencyNormFunc):
    
    frequencyPath = join(featurePath, "frequency")
    utils.makeDir(frequencyPath)
    
    wordsPath = join(featurePath, "words")

    for fn in utils.findFiles(wordsPath):
        wordList = utils.openCSV(wordsPath, fn, valueIndex=0, encoding="utf-8")
        countList = []
        for word in wordList:
            tmp = countObj.getFrequency(word,
                                        frequencyNormFunc,
                                        outOfDictionaryValue=1)
            count, freq, logFreq = tmp
            countList.append("%f,%f,%f" % (count, freq, logFreq))
            
        with open(join(frequencyPath, fn), "w") as fd:
            fd.write("\n".join(countList))
