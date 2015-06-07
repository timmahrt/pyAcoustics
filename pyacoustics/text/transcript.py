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
        data = codecs.open(join(transcriptPath, fn), "r", encoding="utf-8").read()
        dataList = data.split()
        
        codecs.open(join(outputPath, fn), "w", encoding="utf-8").write("\n".join(dataList))


