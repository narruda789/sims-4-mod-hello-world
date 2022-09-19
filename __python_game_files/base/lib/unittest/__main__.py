# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\__main__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 490 bytes
import sys
if sys.argv[0].endswith('__main__.py'):
    import os.path
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + ' -m unittest'
    del os
__unittest = True
from .main import main
main(module=None)