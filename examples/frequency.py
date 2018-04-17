'''
Created on Apr 16, 2018

@author: tmahrt
'''

import io
from os.path import join
from pyacoustics.text import frequency

rootPath = r"/Users/tmahrt/Dropbox/workspace/pyAcoustics/resources"
outputFN = r"/Users/tmahrt/Desktop/buckeye_frequency_counts.csv"

buckeye = frequency.Buckeye(join(rootPath, "buckeye_raw_counts.csv"))
fischer = frequency.Fischer(join(rootPath, "fischer_counts.txt"))
google = frequency.GoogleUnigram(join(rootPath, "google.letter.unigram"))
switchboard = frequency.SwitchboardTim(join(rootPath, "switchboard_counts.txt"))

outputList = []
wordList = buckeye.frequencyDict.keys()
wordList.sort()
sumV = 0
for word in wordList:
    
    # Not including words that were tagged for any reason
    if word[0] == '[':
        continue
    
    sumV += buckeye.getFrequency(word, outOfDictionaryValue=0)[0]
    
    row = [word, ]
    for corpus in [buckeye, fischer, google, switchboard]:
        row.extend(corpus.getFrequency(word, outOfDictionaryValue=""))
    
    rowTxt = ",".join([str(val) for val in row])
    outputList.append(rowTxt)

outputTxt = u"\n".join(outputList)
with io.open(outputFN, 'w') as fd:
    fd.write(outputTxt)
    
print(sumV)

