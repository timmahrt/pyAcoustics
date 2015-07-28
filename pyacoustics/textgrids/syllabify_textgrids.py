'''
Created on Oct 22, 2014

@author: tmahrt
'''

import os
from os.path import join

from praatio import tgio
from pysle import isletool
from pysle import praattools


from pyacoustics.utilities import utils


def correctTextgridTimes(tgPath, threshold):
    
    # Are x and y unique but very very similar
    withinThreshold = lambda x, y: (abs(x - y) < threshold) and (x != y)
    
    outputPath = join(tgPath, "correctsTGs")
    utils.makeDir(outputPath)
    
    for fn in utils.findFiles(tgPath, filterExt=".TextGrid"):
        print(fn)
        tg = tgio.openTextGrid(join(tgPath, fn))
        wordTier = tg.tierDict["words"]
        phoneTier = tg.tierDict["phones"]
        
        for wordEntry in wordTier.entryList:
            
            for i, phoneEntry in enumerate(phoneTier.entryList):
                
                if tgio.intervalOverlapCheck(wordEntry, phoneEntry):
                    
                    start = phoneEntry[0]
                    end = phoneEntry[1]
                    phone = phoneEntry[2]
                    
                    if withinThreshold(wordEntry[0], start):
                        start = wordEntry[0]
                    elif withinThreshold(wordEntry[1], start):
                        start = wordEntry[1]
                    elif withinThreshold(wordEntry[0], end):
                        end = wordEntry[0]
                    elif withinThreshold(wordEntry[1], end):
                        end = wordEntry[1]
                    
                    phoneTier.entryList[i] = (start, end, phone)
        
        tg.save(join(outputPath, fn))


def syllabifyTextgrids(tgPath, islePath):

    isleDict = isletool.LexicalTool(islePath)

    outputPath = join(tgPath, "syllabifiedTGs")
    utils.makeDir(outputPath)
    skipLabelList = ["<VOCNOISE>", "xx", "<SIL>", "{B_TRANS}", '{E_TRANS}']

    for fn in utils.findFiles(tgPath, filterExt=".TextGrid"):

        if os.path.exists(join(outputPath, fn)):
            continue

        tg = tgio.openTextGrid(join(tgPath, fn))
        
        syllableTG = praattools.syllabifyTextgrid(isleDict, tg, "words",
                                                  "phones",
                                                  skipLabelList=skipLabelList)
        
        outputTG = tgio.Textgrid()
        outputTG.addTier(tg.tierDict["words"])
        outputTG.addTier(tg.tierDict["phones"])
#         outputTG.addTier(syllableTG.tierDict["syllable"])
        outputTG.addTier(syllableTG.tierDict["tonic"])
        
        outputTG.save(join(outputPath, fn))

if __name__ == "__main__":
    tmpISLEPath = "/Users/tmahrt/Dropbox/workspace/pysle/test/islev2.txt"
#     correctTextgridTimes(tgPath, 0.0025)

    tmpTGPath = join("/Users/tmahrt/Desktop/experiments/LMEDS_studies",
                     "RPT_English/features/tobi_textgrids/correctsTGs")
    syllabifyTextgrids(tmpTGPath, tmpISLEPath)
