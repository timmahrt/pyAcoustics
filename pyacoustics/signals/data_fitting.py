'''
Created on Jul 6, 2015

@author: tmahrt
'''

from sklearn import mixture

from scipy import stats
import matplotlib.pyplot as plot
import matplotlib.mlab
import numpy as np


def getPDF(ddata, numSamples=50, minV=None, maxV=None):
    
    pdf = stats.gaussian_kde(ddata)
    
    if minV is None:
        minV = min(ddata)
    if maxV is None:
        maxV = max(ddata)
    
    xValues = np.linspace(minV, maxV, numSamples)
    
    yValues = pdf(xValues)
    
    return xValues, yValues


def getBimodalValley(data, numSamples=100, doplot=True):
    '''
    Returns the smallest value between the peaks of a bimodal distribution
    '''

    # Build GMM, fit it to the data, and get GMM parameters
    # The two means are used as the start and end point of a our search
    # for the smallest value between the two distributions.
    
    ncomp = 2  # Could be parameterized later if needed
    
    clf = mixture.GaussianMixture(n_components=ncomp, covariance_type='full')
    clf.fit([[item, ] for item in data])
    ml = clf.means_
    wl = clf.weights_
    cl = clf.covariances_
    ms = [m[0] for m in ml]
    cs = [np.sqrt(c[0][0]) for c in cl]
    ws = [w for w in wl]
    
    # Find the smallest point in the pdf between the means
    startV = int(min(ms))
    endV = int(max(ms))
    
    pdfX, pdfY = getPDF(data, numSamples, startV, endV)
    minY = min(pdfY)
    minX = pdfX[[float(x) for x in pdfY].index(minY)]
    
    # Plot result if requested
    if doplot is True:
        histo = plot.hist(data, numSamples, normed=True)
        for w, m, c in zip(ws, ms, cs):
            normedPDF = matplotlib.mlab.normpdf(histo[1], m, np.sqrt(c))
            plot.plot(histo[1], w * normedPDF, linewidth=3)
        plot.plot(pdfX, pdfY, linewidth=2)
        plot.axvline(minX)
        plot.show()
    
    return minX
