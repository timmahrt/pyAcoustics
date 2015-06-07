'''
Created on Apr 2, 2015

@author: tmahrt
'''

import unittest

from pyacoustics.utilities import statistics


class MedianTest(unittest.TestCase):
    
    MY_LIST = [5, 1, 10, 13, 3, 17, 9, 17]
    
    def test_evenLengthedListCorrect(self):
        median = statistics.getMedian(self.MY_LIST)
        self.assertEqual(median, 9.5)
        
    def test_oddLengthedListCorrect(self):
        median = statistics.getMedian(self.MY_LIST[:-1])
        self.assertEqual(median, 9)
    
    def test_filterOddLengthedListCorrect(self):
        medianList = statistics.medianFilter(self.MY_LIST, 3,
                                             useEdgePadding=True)
        correctList = [5, 5, 10, 10, 13, 9, 17, 17]
        self.assertEqual(medianList, correctList)

if __name__ == '__main__':
    unittest.main()
