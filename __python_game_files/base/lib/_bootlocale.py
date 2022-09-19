# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_bootlocale.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1847 bytes
import sys, _locale
if sys.platform.startswith('win'):

    def getpreferredencoding(do_setlocale=True):
        if sys.flags.utf8_mode:
            return 'UTF-8'
        return _locale._getdefaultlocale()[1]


else:
    try:
        _locale.CODESET
    except AttributeError:
        if hasattr(sys, 'getandroidapilevel'):

            def getpreferredencoding(do_setlocale=True):
                return 'UTF-8'


        else:

            def getpreferredencoding(do_setlocale=True):
                if sys.flags.utf8_mode:
                    return 'UTF-8'
                import locale
                return locale.getpreferredencoding(do_setlocale)


    else:

        def getpreferredencoding(do_setlocale=True):
            if sys.flags.utf8_mode:
                return 'UTF-8'
            result = _locale.nl_langinfo(_locale.CODESET)
            if not result:
                if sys.platform == 'darwin':
                    result = 'UTF-8'
            return result