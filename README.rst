
-------------
pyAcoustics
-------------

A collection of python scripts for extracting and analyzing acoustics from audio files.

.. sectnum::
.. contents::

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

pyacoustics.signals.data_fitting.py requires
`SciPy <http://www.scipy.org/>`_,
`NumPy <http://www.numpy.org/>`_, and
`scikit-learn <http://scikit-learn.org/>`_

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

See the example folders for a few real-world examples using this library.

- examples/split_audio_on_silence.py

    Detects the presence of speech in a recording based on acoustic 
    intensity.  Everything louder than some threshold specified by
    the user is considered speech.
    
- examples/split_audio_on_tone.py

    Detects the presence of pure tones in a recording.  One can use
    this to automatically segment stimuli.  Beeps can be played while
    the speech is being recorded and then later this tool can
    automatically segment the speech, based on the presence of those
    tones.
    
    Also detects speech using a pitch analysis.  Most syllables
    contain some voicing, so a stream of modulating pitch values
    suggests that someone is speaking.  This aspect is not extensively
    tested but it works well for the example files.

- examples/estimate_speech_rate.py

    Calculates the speech rate through a matlab script written by
    `Uwe Reichel <http://www.phonetik.uni-muenchen.de/~reichelu/>`_
    that estimates the location of syllable boundaries.


Citing LMEDS
===============

PyAcoustics is general purpose coding and doesn't need to be cited
but if you would like to, it can be cited like so:

Tim Mahrt. PyAcoustics. https://github.com/timmahrt/pyAcoustics, 2016.


