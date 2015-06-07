# Based on http://www.fon.hum.uva.nl/praat/manual/Script_for_listing_time_--F0_--intensity.html
#


# Pitch and intensity parameters
# male: 50, 350
# female: 75, 450
sampleStep = 0.01
minPitch = 75
maxPitch = 450


# Directory needs a final '/'
# **Both directories need to already exist**
input_directory$ = "/Users/tmahrt/Desktop/experiments/LMEDS_studies/RPT_English/features_test/wav/female/"
output_directory$ = "/Users/tmahrt/Desktop/experiments/LMEDS_studies/RPT_English/features_test/pitch_and_intensity_listings/"

strings = Create Strings as file list... list 'input_directory$'*.wav
numberOfFiles = Get number of strings
for ifile to numberOfFiles
    selectObject: strings
    fileName$ = Get string: ifile
    Read from file: input_directory$ + fileName$
    name$ = fileName$ - ".wav"
	
	sound = selected ("Sound")
	selectObject: sound
	tmin = Get start time
	tmax = Get end time
	
	To Pitch: sampleStep, minPitch, maxPitch
	Rename: "pitch"
	
	selectObject: sound
	To Intensity: minPitch, sampleStep
	Rename: "intensity"
	
	for i to (tmax-tmin)/sampleStep
    		time = tmin + i * sampleStep
    		selectObject: "Pitch pitch"
    		pitch = Get value at time: time, "Hertz", "Linear"
    		selectObject: "Intensity intensity"
    		intensity = Get value at time: time, "Cubic"
    		appendFileLine: "'output_directory$''name$'.txt", fixed$ (time, 2), ",", fixed$ (pitch, 3), ",", fixed$ (intensity, 3)
	endfor


	# Cleanup

	selectObject: "Pitch pitch"
	Remove

	selectObject: "Intensity intensity"
	Remove

	selectObject: sound
	Remove

endfor

selectObject: strings
Remove

