# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\support.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 408 bytes


def is_instance(obj, klass):
    return issubclass(type(obj), klass)


class SomeClass(object):
    class_attribute = None

    def wibble(self):
        pass


class X(object):
    pass


def examine_warnings(func):

    def wrapper():
        with catch_warnings(record=True) as (ws):
            func(ws)

    return wrapper