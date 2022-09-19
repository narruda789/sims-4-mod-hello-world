# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3221 bytes
__all__ = [
 'TestResult', 'TestCase', 'TestSuite',
 'TextTestRunner', 'TestLoader', 'FunctionTestCase', 'main',
 'defaultTestLoader', 'SkipTest', 'skip', 'skipIf', 'skipUnless',
 'expectedFailure', 'TextTestResult', 'installHandler',
 'registerResult', 'removeResult', 'removeHandler']
__all__.extend(['getTestCaseNames', 'makeSuite', 'findTestCases'])
__unittest = True
from .result import TestResult
from .case import TestCase, FunctionTestCase, SkipTest, skip, skipIf, skipUnless, expectedFailure
from .suite import BaseTestSuite, TestSuite
from .loader import TestLoader, defaultTestLoader, makeSuite, getTestCaseNames, findTestCases
from .main import TestProgram, main
from .runner import TextTestRunner, TextTestResult
from .signals import installHandler, registerResult, removeResult, removeHandler
_TextTestResult = TextTestResult

def load_tests(loader, tests, pattern):
    import os.path
    this_dir = os.path.dirname(__file__)
    return loader.discover(start_dir=this_dir, pattern=pattern)