# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\testsentinel.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1366 bytes
import unittest, copy, pickle
from unittest.mock import sentinel, DEFAULT

class SentinelTest(unittest.TestCase):

    def testSentinels(self):
        self.assertEqual(sentinel.whatever, sentinel.whatever, 'sentinel not stored')
        self.assertNotEqual(sentinel.whatever, sentinel.whateverelse, 'sentinel should be unique')

    def testSentinelName(self):
        self.assertEqual(str(sentinel.whatever), 'sentinel.whatever', 'sentinel name incorrect')

    def testDEFAULT(self):
        self.assertIs(DEFAULT, sentinel.DEFAULT)

    def testBases(self):
        self.assertRaises(AttributeError, lambda : sentinel.__bases__)

    def testPickle(self):
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.subTest(protocol=proto):
                pickled = pickle.dumps(sentinel.whatever, proto)
                unpickled = pickle.loads(pickled)
                self.assertIs(unpickled, sentinel.whatever)

    def testCopy(self):
        self.assertIs(copy.copy(sentinel.whatever), sentinel.whatever)
        self.assertIs(copy.deepcopy(sentinel.whatever), sentinel.whatever)


if __name__ == '__main__':
    unittest.main()