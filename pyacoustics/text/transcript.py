'''
Created on Oct 20, 2014

@author: tmahrt
'''

from os.path import join

import io

from pyacoustics.utilities import utils


def toWords(featurePath, outputPath):
    
    utils.makeDir(outputPath)

    transcriptPath = join(featurePath, "txt")

    for fn in utils.findFiles(transcriptPath, filterExt=".txt"):
        fnFullPath = join(transcriptPath, fn)
        with io.open(fnFullPath, "r", encoding="utf-8") as fd:
            data = fd.read()
        dataList = data.split()
        
        with io.open(join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write("\n".join(dataList))
