'''
Created on Oct 20, 2014

@author: tmahrt
'''

import os
from os.path import join
import io

from pyacoustics.utilities import utils


def aggregateFeatures(featurePath, featureList, headerStr=None):
    
    outputDir = join(featurePath, "aggr")
    utils.makeDir(outputDir)
    
    fnList = []
    dataList = []
    
    # Find the files that exist in all features
    for feature in featureList:
        fnSubList = utils.findFiles(join(featurePath, feature),
                                    filterExt=".txt")
        fnList.append(fnSubList)
        
    actualFNList = []
    for featureFN in fnList[0]:
        if all([featureFN in subList for subList in fnList]):
            actualFNList.append(featureFN)
    
    for featureFN in actualFNList:
        dataList = []
        for feature in featureList:
            featureDataList = utils.openCSV(join(featurePath, feature),
                                            featureFN, encoding="utf-8")
            dataList.append([",".join(row) for row in featureDataList])
        
        name = os.path.splitext(featureFN)[0]
        
        dataList.insert(0, [name for _ in range(len(dataList[0]))])
        tDataList = utils.safeZip(dataList, enforceLength=True)
        outputList = [",".join(row) for row in tDataList]
        outputTxt = "\n".join(outputList)
        
        outputFN = join(outputDir, name + ".csv")
        with io.open(outputFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)
        
    # Cat all files together
    aggrOutput = []
    
    if headerStr is not None:
        aggrOutput.append(headerStr)
    
    for fn in utils.findFiles(outputDir, filterExt=".csv"):
        if fn == "all.csv":
            continue
        with io.open(join(outputDir, fn), "r", encoding='utf-8') as fd:
            aggrOutput.append(fd.read())
    
    with io.open(join(outputDir, "all.csv"), "w", encoding='utf-8') as fd:
        fd.write("\n".join(aggrOutput))
