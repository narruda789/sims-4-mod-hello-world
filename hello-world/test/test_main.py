from unittest import TestCase

from main import say_hello


class TestMain(TestCase):
    def test_running_tests_works(self):
        self.assertTrue(True)

    def test_say_hello(self):
        say_hello()
