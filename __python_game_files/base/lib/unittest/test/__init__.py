# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\__init__.py
# Compiled at: 2013-04-05 19:16:42
# Size of source mod 2**32: 606 bytes
import os, sys, unittest
here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def suite():
    suite = unittest.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith('test') and fn.endswith('.py'):
            modname = 'unittest.test.' + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))

    suite.addTest(loader.loadTestsFromName('unittest.test.testmock'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')