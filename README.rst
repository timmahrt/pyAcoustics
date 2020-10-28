
-------------
pyAcoustics
-------------

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?
   :target: http://opensource.org/licenses/MIT

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
    
- Mask speech with speech shaped noise::

    pyacoustics.speech_filters.speech_shaped_noise.batchMaskSpeakerData()

- And more!


Major revisions
================

Ver 1.0 (June 7, 2015)

- first public release.


Features as they are added
===========================

Mask speech with speech shaped noise
(March 21, 2016)

Find syllable nuclei/estimate speech rate using Uwe Reichel's matlab code
(July 29, 2015) 

Find the valley bottom between peaks (July 7th, 2015)

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

If you on Windows, you can use the installer found here (check that it is up to date though)
`Windows installer <http://www.timmahrt.com/python_installers>`_

PyAcoustics is on pypi and can be installed or upgraded from the command-line shell with pip like so::

    python -m pip install pyacoustics --upgrade

Otherwise, to manually install, after downloading the source from github, from a command-line shell, navigate to the directory containing setup.py and type::

    python setup.py install

If python is not in your path, you'll need to enter the full path e.g.::

	C:\Python36\python.exe setup.py install

    
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


Acknowledgements
=================

PyAcoustics is an ongoing collection of code with contributions from a
number of projects worked on over several years.  Development of various
aspects of PyAcoustics was possible thanks to
NSF grant **IIS 07-03624**
to Jennifer Cole and Mark Hasegawa-Johnson,
NSF grant BCS **12-51343**
to Jennifer Cole, José Hualde, and Caroline Smith, and
NSF grant
**IBSS SMA 14-16791** to Jennifer Cole, Nancy McElwain, and Daniel Berry.
