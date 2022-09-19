# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\cp65001.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1149 bytes
import codecs, functools
if not hasattr(codecs, 'code_page_encode'):
    raise LookupError('cp65001 encoding is only available on Windows')
encode = functools.partial(codecs.code_page_encode, 65001)
_decode = functools.partial(codecs.code_page_decode, 65001)

def decode(input, errors='strict'):
    return codecs.code_page_decode(65001, input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = _decode


class StreamWriter(codecs.StreamWriter):
    encode = encode


class StreamReader(codecs.StreamReader):
    decode = _decode


def getregentry():
    return codecs.CodecInfo(name='cp65001',
      encode=encode,
      decode=decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)