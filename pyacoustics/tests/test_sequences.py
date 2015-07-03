'''
Created on Jul 3, 2015

@author: tmahrt
'''

import unittest

from pyacoustics.utilities import sequences


class invertIntervalList(unittest.TestCase):
    
    LIST_A = [(5, 6), (10, 13), (14, 16)]
    LIST_B = [(0, 1), (5, 6), (10, 13), (14, 16)]
    
    def test_startsAtZero(self):
        invertedList = sequences.invertIntervalList(self.LIST_B)
        correctAnswer = [(1, 5), (6, 10), (13, 14)]
        self.assertEqual(invertedList, correctAnswer)

    def test_startsAtNonZero(self):
        invertedList = sequences.invertIntervalList(self.LIST_A)
        correctAnswer = [(0, 5), (6, 10), (13, 14)]
        self.assertEqual(invertedList, correctAnswer)
        
    def test_maxValue(self):
        invertedList = sequences.invertIntervalList(self.LIST_B, maxValue=20)
        correctAnswer = [(1, 5), (6, 10), (13, 14), (16, 20)]
        self.assertEqual(invertedList, correctAnswer)
    
    def test_minValue(self):
        invertedList = sequences.invertIntervalList(self.LIST_A, minValue=3)
        correctAnswer = [(3, 5), (6, 10), (13, 14)]
        self.assertEqual(invertedList, correctAnswer)
        
    def test_twiceInverted(self):
        invertedList = sequences.invertIntervalList(self.LIST_A, 0, 20)
        twiceInvList = sequences.invertIntervalList(invertedList, 0, 20)
        self.assertEqual(self.LIST_A, twiceInvList)

if __name__ == '__main__':
    unittest.main()
