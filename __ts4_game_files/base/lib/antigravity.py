# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\antigravity.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 493 bytes
import webbrowser, hashlib
webbrowser.open('https://xkcd.com/353/')

def geohash(latitude, longitude, datedow):
    h = hashlib.md5(datedow).hexdigest()
    p, q = ['%f' % float.fromhex('0.' + x) for x in (h[:16], h[16:32])]
    print('%d%s %d%s' % (latitude, p[1:], longitude, q[1:]))