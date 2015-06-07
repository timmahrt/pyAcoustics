
---------
pyAcoustics
---------

A collection of python scripts for extracting and analyzing acoustics from audio files.


Common Use Cases
================

What can you do with this library?

- Extract pitch and intensity::

    pyacoustics.intensity_and_pitch.praat_pi.getPraatPitchAndIntensity()

- Extract segments of a wav file::

    pyacoustics.signals.audio_scripts.getSubwav()

- Perform simple manipulations on wav files::

    pyacoustics.signals.resampleAudio()

    pyacoustics.signals.splitStereoAudio()

- Split audio files on segments of silence or on pure tones::

    pyacoustics.speech_detection.split_on_tone.splitFileOnTone()

- Programmatically manipulate pitch or duration of a file::

    pyacoustics.morph.morph_utils.praat_pitch()

- And more!


Requirements
================

Many of the individual features require different packages.  If you aren't using those
packages then you don't need to install the dependencies.

pyacoustics.intensity_and_pitch.praat_pi requires 
`praat <http://www.fon.hum.uva.nl/praat/>`_

pyacoustics.intensity_and_pitch.get_f0 requires the ESPS getF0 function as implemented 
by `Snack <http://www.speech.kth.se/snack/>`_ although I recall having difficulty 
installing it.

pyacoustics.speech_rate/dictionary_estimate.py requires my library 
`psyle <https://github.com/timmahrt/pysle>`_

My praatIO library is used extensively and can be downloaded 
`here <https://github.com/timmahrt/praatIO>`_


Installation
================

From a command-line shell, navigate to the directory this is located in 
and type::

	python setup.py install

If python is not in your path, you'll need to enter the full path e.g.::

	C:\Python27\python.exe setup.py install

	
Example usage
================

TODO

