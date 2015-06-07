numSteps = %(num_steps)s

Read from file... %(input_dir)s/%(input_name)s.wav

for iStep to numSteps - 1
    zeroedI = iStep
    
    Read from file... %(pitch_dir)s/%(input_name)s_'zeroedI'.PitchTier
    select Sound %(input_name)s
    To Manipulation... 0.01 %(pitch_lower_bound)d %(pitch_upper_bound)d
    
    select PitchTier %(input_name)s_'zeroedI'
    plus Manipulation %(input_name)s
    Replace pitch tier
    
    select Manipulation %(input_name)s
    Get resynthesis (overlap-add)
    Save as WAV file... %(output_dir)s/%(output_name)s_'zeroedI'.wav
    Remove
    
    select Manipulation %(input_name)s
    Remove
    select PitchTier %(input_name)s_'zeroedI'
    Remove
endfor

select Sound %(input_name)s
Remove