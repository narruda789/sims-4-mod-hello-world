# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_sitebuiltins.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3218 bytes
import sys

class Quitter(object):

    def __init__(self, name, eof):
        self.name = name
        self.eof = eof

    def __repr__(self):
        return 'Use %s() or %s to exit' % (self.name, self.eof)

    def __call__(self, code=None):
        try:
            sys.stdin.close()
        except:
            pass

        raise SystemExit(code)


class _Printer(object):
    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        import os
        self._Printer__name = name
        self._Printer__data = data
        self._Printer__lines = None
        self._Printer__filenames = [os.path.join(dir, filename) for dir in dirs for filename in files]

    def __setup(self):
        if self._Printer__lines:
            return
        data = None
        for filename in self._Printer__filenames:
            try:
                with open(filename, 'r') as (fp):
                    data = fp.read()
                break
            except OSError:
                pass

        if not data:
            data = self._Printer__data
        self._Printer__lines = data.split('\n')
        self._Printer__linecnt = len(self._Printer__lines)

    def __repr__(self):
        self._Printer__setup()
        if len(self._Printer__lines) <= self.MAXLINES:
            return '\n'.join(self._Printer__lines)
        return 'Type %s() to see the full %s text' % ((self._Printer__name,) * 2)

    def __call__(self):
        self._Printer__setup()
        prompt = 'Hit Return for more, or q (and Return) to quit: '
        lineno = 0
        while 1:
            try:
                for i in range(lineno, lineno + self.MAXLINES):
                    print(self._Printer__lines[i])

            except IndexError:
                break
            else:
                lineno += self.MAXLINES
                key = None
                while key is None:
                    key = input(prompt)
                    if key not in ('', 'q'):
                        key = None

                if key == 'q':
                    break


class _Helper(object):

    def __repr__(self):
        return 'Type help() for interactive help, or help(object) for help about object.'

    def __call__(self, *args, **kwds):
        import pydoc
        return (pydoc.help)(*args, **kwds)