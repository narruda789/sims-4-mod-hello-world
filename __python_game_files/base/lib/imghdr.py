# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\imghdr.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3963 bytes
from os import PathLike
__all__ = [
 'what']

def what(file, h=None):
    f = None
    try:
        if h is None:
            if isinstance(file, (str, PathLike)):
                f = open(file, 'rb')
                h = f.read(32)
            else:
                location = file.tell()
                h = file.read(32)
                file.seek(location)
        for tf in tests:
            res = tf(h, f)
            if res:
                return res

    finally:
        if f:
            f.close()


tests = []

def test_jpeg(h, f):
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'


tests.append(test_jpeg)

def test_png(h, f):
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'


tests.append(test_png)

def test_gif(h, f):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'


tests.append(test_gif)

def test_tiff(h, f):
    if h[:2] in (b'MM', b'II'):
        return 'tiff'


tests.append(test_tiff)

def test_rgb(h, f):
    if h.startswith(b'\x01\xda'):
        return 'rgb'


tests.append(test_rgb)

def test_pbm(h, f):
    if len(h) >= 3:
        if h[0] == ord(b'P'):
            if h[1] in b'14':
                if h[2] in b' \t\n\r':
                    return 'pbm'


tests.append(test_pbm)

def test_pgm(h, f):
    if len(h) >= 3:
        if h[0] == ord(b'P'):
            if h[1] in b'25':
                if h[2] in b' \t\n\r':
                    return 'pgm'


tests.append(test_pgm)

def test_ppm(h, f):
    if len(h) >= 3:
        if h[0] == ord(b'P'):
            if h[1] in b'36':
                if h[2] in b' \t\n\r':
                    return 'ppm'


tests.append(test_ppm)

def test_rast(h, f):
    if h.startswith(b'Y\xa6j\x95'):
        return 'rast'


tests.append(test_rast)

def test_xbm(h, f):
    if h.startswith(b'#define '):
        return 'xbm'


tests.append(test_xbm)

def test_bmp(h, f):
    if h.startswith(b'BM'):
        return 'bmp'


tests.append(test_bmp)

def test_webp(h, f):
    if h.startswith(b'RIFF'):
        if h[8:12] == b'WEBP':
            return 'webp'


tests.append(test_webp)

def test_exr(h, f):
    if h.startswith(b'v/1\x01'):
        return 'exr'


tests.append(test_exr)

def test():
    import sys
    recursive = 0
    if sys.argv[1:]:
        if sys.argv[1] == '-r':
            del sys.argv[1:2]
            recursive = 1
    try:
        if sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        else:
            testall(['.'], recursive, 1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)


def testall(list, recursive, toplevel):
    import sys, os
    for filename in list:
        if os.path.isdir(filename):
            print((filename + '/:'), end=' ')
            if recursive or toplevel:
                print('recursing down:')
                import glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            else:
                print('*** directory (use -r) ***')
        else:
            print((filename + ':'), end=' ')
            sys.stdout.flush()
            try:
                print(what(filename))
            except OSError:
                print('*** not found ***')


if __name__ == '__main__':
    test()