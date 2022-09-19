# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\__main__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 614 bytes
import os, unittest

def load_tests(loader, standard_tests, pattern):
    this_dir = os.path.dirname(__file__)
    pattern = pattern or 'test_*.py'
    top_level_dir = os.path.dirname(os.path.dirname(this_dir))
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern, top_level_dir=top_level_dir)
    standard_tests.addTests(package_tests)
    return standard_tests


if __name__ == '__main__':
    unittest.main()