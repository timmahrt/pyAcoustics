'''
Created on Mar 18, 2016

@author: timmahrt

*Preface: I'm not an expert in noise.  What I've written here is just how I
(naively) understand this topic.

The following code is used for generating speech-shaped noise and masking
speech using it.  Speech-shaped noise is white noise with the same spectral
properties as speech.  As individual people have different spectral qualities,
speech shaped noise should ideally be generated for each individual.

The process:
- first, speech shaped noise is generated for a speaker's
  recordings via generateNoise()
- second, the speaker's data is then masked using the generated noise
  via maskSpeech()

The alternative process:
- if the files used to generate the noise are the same files that need to
  be masked, use the convenience function batchMaskSpeakerData()

Some guidelines:
- at least 3 minutes of speech should be used.  If less than that is used,
  the noise may contain harmonic components
- silences can exist in the input

Requires scipy and numpy

See the bottom of this file for an example usage.
'''

import os
from os.path import join

import functools
import wave

import numpy as np
from scipy.io import wavfile
from scipy import signal
from numpy import fft

###########################
# start of pambox code
# Copyright (c) 2014, Alexandre Chabot-Leclerc
# See LICENSE file for more information
###########################


def _dbspl(x, ac=False, offset=0.0):
    """Computes RMS value of signal in dB.

    By default, a signal with an RMS value of 1 will have a level of 0 dB
    SPL.

    Parameters
    ----------
    x : array_like
        Signal for which to caculate the sound-pressure level.
    ac : bool
        Consider only the AC component of the signal, i.e. the mean is
        removed (Default value =  False)
    offset : float
        Reference to convert between RMS and dB SPL.  (Default value = 0.0)
    axis : int
        Axis on which to compute the SPL value (Default value = -1, last axis)

    Returns
    -------
    ndarray
        Sound-pressure levels.

    References
    ----------
    .. [1] Auditory Modeling Toolbox, Peter L. Soendergaard
      B. C. J. Moore. An Introduction to the Psychology of Hearing. Academic
      Press, 5th edition, 2003.

    See also
    --------
    setdbspl
    rms
    """
    x = np.asarray(x)
    return 20. * np.log10(_rms(x, ac)) + float(offset)


def _read_wav_as_float(path):
    """Reads a wavefile as a float.
    Parameters
    ----------
    path : string
        Path to the wave file.
    Returns
    -------
    wav : ndarray
    """
    _, signal = wavfile.read(path)
    if np.issubdtype(signal.dtype, np.integer):
        # Integer division here.  The '1.0' converts the numbers to float.
        return signal.T / (1.0 * np.abs(np.iinfo(signal.dtype).min))
    return signal.T
    

def _write_wav(fname, fs, x, normalize=False):
    """Writes floating point numpy array to 16 bit wavfile.

    Convenience wrapper around the scipy.io.wavfile.write function.

    The '.wav' extension is added to the file if it is not part of the
    filename string.

    Inputs of type `np.float` are converted to `int16` before writing to file.

    Parameters
    ----------
    fname : string
        Filename with path.
    fs : int
        Sampling frequency.
    x : array_like
        Signal with the shape N_channels x Length
    normalize : bool
        Scale the signal such that its maximum value is one.

    Returns
    -------
    None

    """
    # Make sure that the channels are the second dimension
    fs = np.int(fs)
    if not fname.endswith('.wav'):
        fname += '.wav'

    if x.shape[0] <= 2:
        x = x.T

    if np.issubdtype(x.dtype, np.float) and normalize:
        scaled = (x / np.max(np.abs(x)) * (2 ** 15 - 1))
    elif np.issubdtype(x.dtype, np.float):
        scaled = x * (2 ** 15 - 1)
    else:
        scaled = x
    wavfile.write(fname, fs, scaled.astype('int16'))


def _rms(x, ac=False, axis=-1):
    """Calculates the RMS value of a signal.

    Parameters
    ----------
    x : array_like
        Signal.
    ac : bool
        Consider only the AC component of the signal. (Default value = False)
    axis :
        Axis on which to calculate the RMS value. The default is to calculate
        the RMS on the last dimensions, i.e. axis = -1.

    Returns
    -------
    ndarray
        RMS value of the signal.

    """
    x = np.asarray(x)
    if ac:
        if x.ndim > 1 and axis == -1:
            x_mean = x.mean(axis=axis)[..., np.newaxis]
        else:
            x_mean = x.mean(axis=axis)
        return np.linalg.norm((x - x_mean) / np.sqrt(x.shape[axis]), axis=axis)
    else:
        return np.linalg.norm(x / np.sqrt(x.shape[axis]), axis=axis)


def _mix_noise(clean, noise, sent_level, snr=None):
    """Mix a signal signal noise at a given signal-to-noise ratio.

    Parameters
    ----------
    clean : ndarray
        Clean signal.
    noise : ndarray
        Noise signal.
    sent_level : float
        Sentence level, in dB SPL.
    snr :
        Signal-to-noise ratio at which to mix the signals, in dB. If snr is
        `None`,  no noise is mixed with the signal (Default value = None)

    Returns
    -------
    tuple of ndarrays
        Returns the clean signal, the mixture, and the noise.

    """

    # Pick a random section of the noise
    n_clean = len(clean)
    n_noise = len(noise)
    if n_noise > n_clean:
        start_idx = np.random.randint(n_noise - n_clean)
        noise = noise[start_idx:start_idx + n_clean]

    if snr is not None:
        # Get speech level and set noise level accordingly
        # clean_level = utils.dbspl(clean)
        # noise = utils.setdbspl(noise, clean_level - snr)
        noise = noise / _rms(noise) * 10 ** ((sent_level - snr) / 20)
        mix = clean + noise
    else:
        mix = clean

    return clean, mix, noise

        
def _noise_from_signal(x, fs=40000, keep_env=False):
    """Create a noise with same spectrum as the input signal.

    Parameters
    ----------
    x : array_like
        Input signal.
    fs : int
         Sampling frequency of the input signal. (Default value = 40000)
    keep_env : bool
         Apply the envelope of the original signal to the noise. (Default
         value = False)

    Returns
    -------
    ndarray
        Noise signal.

    """
    x = np.asarray(x)
    n_x = x.shape[-1]
    n_fft = next_pow_2(n_x)
    X = fft.rfft(x, next_pow_2(n_fft))
    # Randomize phase.
    noise_mag = np.abs(X) * np.exp(
        2 * np.pi * 1j * np.random.random(X.shape[-1]))
    noise = np.real(fft.irfft(noise_mag, n_fft))
    out = noise[:n_x]

    if keep_env:
        env = np.abs(signal.hilbert(x))
        [bb, aa] = signal.butter(6, 50 / (fs / 2))  # 50 Hz LP filter
        env = signal.filtfilt(bb, aa, env)
        out *= env

    return out


def next_pow_2(x):
    """Calculates the next power of 2 of a number."""
    return int(pow(2, np.ceil(np.log2(x))))
    

###########################
# end of pambox code
###########################


class NotListException(Exception):

    def __str__(self):
        return "Error.  First argument must be a list of file names."


class InconsistentFramerateException(Exception):

    def __init__(self, wavFNList, framerateList):
        super(InconsistentFramerateException, self).__init__()
        
        self.framerateDict = {}
        
        framerateSet = list(set(framerateList))
        for framerate in framerateSet:
            self.framerateDict[framerate] = []
        
        for wavFN, framerate in zip(wavFNList, framerateList):
            self.framerateDict[framerate].append(wavFN)

    def __str__(self):
        
        outputStr = "Error.  All wave files must have the same framerate"
        
        for framerate, fnList in self.framerateDict.items():
            outputStr += "\n%s: %s" % (framerate, repr(fnList))
        
        return outputStr


def _getFramerate(wavFN):
    
    audiofile = wave.open(wavFN, "r")
    params = audiofile.getparams()
    
    return params[2]


def _getDuration(waveFN):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    audiofile = wave.open(waveFN, "r")
    
    params = audiofile.getparams()
    framerate = params[2]
    nframes = params[3]
    
    duration = float(nframes) / framerate
    return duration


def _getMatchFunc(pattern):
    '''
    An unsophisticated pattern matching function
    '''
    
    # '#' Marks word boundaries, so if there is more than one we need to do
    #    something special to make sure we're not mis-representings them
    assert(pattern.count('#') < 2)

    def startsWith(subStr, fullStr):
        return fullStr[:len(subStr)] == subStr
            
    def endsWith(subStr, fullStr):
        return fullStr[-1 * len(subStr):] == subStr
    
    def inStr(subStr, fullStr):
        return subStr in fullStr

    # Selection of the correct function
    if pattern[0] == '#':
        pattern = pattern[1:]
        cmpFunc = startsWith
        
    elif pattern[-1] == '#':
        pattern = pattern[:-1]
        cmpFunc = endsWith
        
    else:
        cmpFunc = inStr
    
    return functools.partial(cmpFunc, pattern)


def findFiles(path, filterPaths=False, filterExt=None, filterPattern=None,
              skipIfNameInList=None, stripExt=False, addPath=False):
    '''
    The primary use is to find files in a folder spoken by the same speaker
    
    Feed the input of findFiles into generateSpeechShapedNoise() as the first
    argument.
    '''
    fnList = os.listdir(path)
       
    if filterPaths is True:
        fnList = [folderName for folderName in fnList
                  if os.path.isdir(os.path.join(path, folderName))]

    if filterExt is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        fnList = [fn for fn, name, ext in splitFNList if ext == filterExt]
        
    if filterPattern is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        matchFunc = _getMatchFunc(filterPattern)
        fnList = [fn for fn, name, ext in splitFNList if matchFunc(name)]
    
    if skipIfNameInList is not None:
        targetNameList = [os.path.splitext(fn)[0] for fn in skipIfNameInList]
        fnList = [fn for fn in fnList
                  if os.path.splitext(fn)[0] not in targetNameList]
    
    if stripExt is True:
        fnList = [os.path.splitext(fn)[0] for fn in fnList]
        
    if addPath is True:
        fnList = [join(path, fn) for fn in fnList]
    
    fnList.sort()
    return fnList

    
def generateNoise(inputFNList, outputFN, outputDuration=None):
    '''
    Generates a file of random noise within the spectrum provided by the input
    
    The input should contain at least 3 minutes of speech for best results.
    Silences can exist in with the speech.  Multiple files can be considered
    for one speech shaped noise generation.
    
    With less than 3 minutes, the speech shaped noise might contain
    harmonic components.
    
    The output will have the same duration as the input, but if you don't need
    such a long file, you can truncate the output.
    '''
    
    # Input must be a list
    if not isinstance(inputFNList, list):
        raise NotListException()
    
    # Verify that all files have the same framerate
    framerateList = [_getFramerate(fn) for fn in inputFNList]
    framerate = framerateList[0]
    if not all([tmpFramerate == framerate for tmpFramerate in framerateList]):
        raise InconsistentFramerateException(inputFNList, framerateList)
    
    outputPath = os.path.split(outputFN)[0]
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
    
    # Append the frames across all audio files
    audioFrames = []
    for fn in inputFNList:
        audioFrames.extend(_read_wav_as_float(fn))
    
    # Get the speech shaped noise
    # I'm not sure what the third argument does, but setting it
    # to True makes the output sound horrible in my experience.
    noiseFrames = _noise_from_signal(audioFrames,
                                     framerate,
                                     False)
    
    # Crop the file if specified by parameter /outputDuration/
    if outputDuration is not None:
        duration = len(noiseFrames) / framerate
        if duration < outputDuration:
            errMsg = ("Duration shorter than requested for file '%s'. "
                      "Not cropping output.")
            print(errMsg % outputDuration)
        else:
            noiseFrames = noiseFrames[:outputDuration * framerate]
    
    _write_wav(outputFN, framerate, noiseFrames, True)


def maskSpeech(inputFN, noiseFN, outputFN, snr):
    '''
    Mask the input file with the noise file with level snr (dB).
    
    noise file can be generated with generateSpeechShapedNoise()
    
    Interesting snr values, that increasingly distort the speech,
    are 3 to -11.  See Aubanel et al 2014 for more information.
    '''
    
    outputPath = os.path.split(outputFN)[0]
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
        
    audioFrames = _read_wav_as_float(inputFN)
    noiseFrames = _read_wav_as_float(noiseFN)
    clean_level = _dbspl(audioFrames)
    framerate = _getFramerate(inputFN)
    noiseFramerate = _getFramerate(inputFN)
    
    if framerate != noiseFramerate:
        InconsistentFramerateException([inputFN, noiseFN],
                                       [framerate, noiseFramerate])
    
    outputFrames = _mix_noise(audioFrames[:],
                              noiseFrames[:],
                              clean_level,
                              snr)[1]
    
    print outputFN
    _write_wav(outputFN, framerate, outputFrames, True)

    
def batchMaskSpeakerData(fnList, noiseProfileFN, outputPath, snrList,
                         regenerateNoiseProfile=True):
    '''
    Given a set of speech from a single speaker, mask each file with noise
    
    Create the speech shaped noise by combining all the speech files.
    
    This is a convenience function that combines the functionality of
    generateNoise() and maskSpeech()
    '''

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)
    
    # Generate the noise profile
    if regenerateNoiseProfile is True or not os.path.exists(noiseProfileFN):
        generateNoise(fnList, noiseProfileFN)
    
    # Mask the speech files
    for snr in snrList:
        snrOutputPath = join(outputPath, repr(snr))
        if not os.path.exists(snrOutputPath):
            os.mkdir(snrOutputPath)
        
        for fnFullPath in fnList:
            fn = os.path.split(fnFullPath)[1]
            maskSpeech(fnFullPath,
                       noiseProfileFN,
                       join(snrOutputPath, fn),
                       snr)


if __name__ == "__main__":

    # Example usage
    _inputPath = (r"C:\Users\Tim\Desktop\cleaned_wavs")

    _noiseFN = r"C:\Users\Tim\Desktop\noise_profiles\amelia_ssn.wav"
    _outputPath = r"C:\Users\Tim\Desktop\noise_filtered_speech"
    
    # You can easily filter each audio file with different snrs by using this
    # list.  Each will be output to an appropriately labeled subfolder of
    # the output path
    _snrList = [-3, ]
    
    # You can manually create a list or use this search function to find
    # all of the files produced by the same speaker which you want to
    # create a speech shaped noise for and which you subsequently want
    # to mask using that noise.
    _fnList = findFiles(_inputPath, filterExt=".wav", addPath=True)
    batchMaskSpeakerData(_fnList, _noiseFN, _outputPath, _snrList)

