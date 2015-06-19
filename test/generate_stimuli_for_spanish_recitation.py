'''
Created on May 13, 2015

@author: tmahrt
'''
import os
from pyacoustics.utilities import utils

def blah():
    
    path = "/Users/tmahrt/Dropbox/Rhetorical Stress Manipulated Files"
    
    list1 = []
    i = 0
    for fn in utils.findFiles(path, filterExt=".wav"):
        
        name = os.path.splitext(fn)[0]
        
        page = "audio_with_response_page 10 [%s]" % name
        
        print(page)
    
    
        
    
if __name__ == "__main__":
    
    blah()
