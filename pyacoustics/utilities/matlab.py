'''
Created on Jul 28, 2015

@author: tmahrt
'''

import subprocess

from pyacoustics.utilities import error_utils


def runMatlabFunction(command, matlabEXE, matlabCodePathList, printCmd=False):
    error_utils.checkForApplication(matlabEXE)
    
    pathCode = "".join(["addpath('%s');" % matlabCodePath
                       for matlabCodePath in matlabCodePathList])
    exitCode = "exit;"
    
    codeSequence = pathCode + command + exitCode

    if printCmd is True:
        print(matlabEXE + ' -nosplash -nodesktop -r "%s"' % codeSequence)
    myProcess = subprocess.Popen([matlabEXE, "-nosplash",
                                  "-nodesktop", "-r", codeSequence])
    if myProcess.wait():
        exit()  # Something has gone wrong (an error message should be printed)
