'''
Created on Apr 3, 2015

@author: tmahrt
'''

import math


def rms(intensityValues):
    intensityValues = [val ** 2 for val in intensityValues]
    meanVal = sum(intensityValues) / len(intensityValues)
    return math.sqrt(meanVal)


def linspace(start, stop, n):
    if n == 1:
        return [stop, ]
    h = (stop - start) / float(n - 1)
    return [start + h * i for i in range(n)]


def orderOfMagnitude(val):
    return int(math.floor(math.log10(val)))
