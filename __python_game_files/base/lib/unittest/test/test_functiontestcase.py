# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\test_functiontestcase.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5688 bytes
import unittest
from unittest.test.support import LoggingResult

class Test_FunctionTestCase(unittest.TestCase):

    def test_countTestCases(self):
        test = unittest.FunctionTestCase(lambda : None)
        self.assertEqual(test.countTestCases(), 1)

    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')
            raise RuntimeError('raised by setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')

        expected = [
         'startTest', 'setUp', 'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            raise RuntimeError('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = [
         'startTest', 'setUp', 'test', 'tearDown',
         'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            self.fail('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = [
         'startTest', 'setUp', 'test', 'tearDown',
         'addFailure', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')
            raise RuntimeError('raised by tearDown')

        expected = [
         'startTest', 'setUp', 'test', 'tearDown', 'addError',
         'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_id(self):
        test = unittest.FunctionTestCase(lambda : None)
        self.assertIsInstance(test.id(), str)

    def test_shortDescription__no_docstring(self):
        test = unittest.FunctionTestCase(lambda : None)
        self.assertEqual(test.shortDescription(), None)

    def test_shortDescription__singleline_docstring(self):
        desc = 'this tests foo'
        test = unittest.FunctionTestCase((lambda : None), description=desc)
        self.assertEqual(test.shortDescription(), 'this tests foo')


if __name__ == '__main__':
    unittest.main()