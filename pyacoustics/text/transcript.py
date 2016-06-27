'''
Created on Oct 20, 2014

@author: tmahrt
'''

from os.path import join

import codecs

from pyacoustics.utilities import utils


def toWords(featurePath, outputPath):
    
    utils.makeDir(outputPath)

    transcriptPath = join(featurePath, "txt")

    for fn in utils.findFiles(transcriptPath, filterExt=".txt"):
        fnFullPath = join(transcriptPath, fn)
        with codecs.open(fnFullPath, "r", encoding="utf-8") as fd:
            data = fd.read()
        dataList = data.split()
        
        with codecs.open(join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write("\n".join(dataList))
