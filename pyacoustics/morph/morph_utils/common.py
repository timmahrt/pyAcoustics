'''
Created on Apr 2, 2015

@author: tmahrt
'''

from os.path import join
import subprocess

from praatio import tgio


def getIntervals(fn, tierName, filterFunc=None):
    '''
    Get information about the 'extract' tier, used by several merge scripts
    '''
    
    if filterFunc is None:
        filterFunc = lambda x: True
    
    tg = tgio.openTextGrid(fn)
    tier = tg.tierDict[tierName]
    
    entryList = tier.entryList
    if filterFunc is not None:
        entryList = [entry for entry in entryList if filterFunc(entry)]
              
    return entryList


def loadPraatTemplate(fn, praatDirectory=None):
    '''
    Convenience function for loading praat scripts
    '''
    if praatDirectory is None:
        praatDirectory = "../praat_templates"
    return open(join(praatDirectory, fn), "r").read()


def runPraatScript(praatExe, scriptPath):
    
    print("%s %s" % (praatExe, scriptPath))
    subprocess.call([praatExe, scriptPath])
