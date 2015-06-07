'''
Created on Jun 7, 2015

@author: tmahrt
'''

import os


class ApplicationNotFound(Exception):
    
    def __init__(self, applicationName):
        super(ApplicationNotFound, self).__init__()
        self.applicationName = applicationName
        
    def __str__(self):
        return "Application (%s) does not exist" % self.applicationName


def checkForApplication(application):
    if not os.path.exists(application):
        raise ApplicationNotFound(application)
