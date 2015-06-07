# Based on http://www.fon.hum.uva.nl/praat/manual/Script_for_listing_time_--F0_--intensity.html
#


# Pitch and intensity parameters
# male: 50, 350
# female: 75, 450
# sampleStep: 0.01 
sampleStep = %(sample_step)f 
minPitch = %(min_pitch)f
maxPitch = %(max_pitch)f


# Directory needs a final '/'
# **Both directories need to already exist**
input_directory$ = "%(input_directory)s"
output_directory$ = "%(output_directory)s"

fileName$ = "%(file_name)s"
Read from file: input_directory$ + fileName$
name$ = fileName$ - ".wav"

#Pitch settings: minPitch, maxPitch, "Hertz", "autocorrelation", "automatic"

sound = selected ("Sound")
selectObject: sound
tmin = Get start time
tmax = Get end time

To Pitch: 0.001, minPitch, maxPitch
Rename: "pitch"

selectObject: sound
To Intensity: minPitch, 0.001, 1
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


