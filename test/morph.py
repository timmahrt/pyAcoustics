
from os.path import join

import praatio

from pyacoustics.morph import praat_pitch
from pyacoustics.morph import morph_duration

path="/Users/tmahrt/Desktop/Johns_prosody_morph"
minPitch = 50
maxPitch = 350

# for fn in ["1.TextGrid", "2.TextGrid"]:
#     
#     tg = praatio.openTextGrid(join(path, fn))
#     for tierName in tg.tierNameList:
#         tier = tg.tierDict[tierName]
#         
#         newEntryList = [entry for entry in tier.entryList if "sp" not in entry[2]]
#         tg.replaceTier(tierName, newEntryList)
#         
#     tg.save(join(path, "mod_"+fn))
        
praat_pitch.f0Morph(path=path, 
                    fromFN="2.wav",
                    toFN="1.wav",
                    numSteps=1,
                    tierName="word",
                    doPlotPitchSteps=False,
                    fromMinPitch=minPitch,
                    fromMaxPitch=maxPitch,
                    toMinPitch=minPitch,
                    toMaxPitch=maxPitch,
                    loadPitchFlag=False,
                    praatExe="/Users/tmahrt/Dropbox/workspace/AcousticFeatureExtractionSuite/praatScripts",
                    praatScriptDir="/Users/tmahrt/Dropbox/workspace/AcousticFeatureExtractionSuite/praatScripts")


