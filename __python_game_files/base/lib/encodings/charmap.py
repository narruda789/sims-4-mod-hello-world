# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\charmap.py
# Compiled at: 2011-04-08 23:53:23
# Size of source mod 2**32: 2153 bytes
import codecs

class Codec(codecs.Codec):
    encode = codecs.charmap_encode
    decode = codecs.charmap_decode


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict', mapping=None):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.mapping = mapping

    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, self.mapping)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def __init__(self, errors='strict', mapping=None):
        codecs.IncrementalDecoder.__init__(self, errors)
        self.mapping = mapping

    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, self.mapping)[0]


class StreamWriter(Codec, codecs.StreamWriter):

    def __init__(self, stream, errors='strict', mapping=None):
        codecs.StreamWriter.__init__(self, stream, errors)
        self.mapping = mapping

    def encode(self, input, errors='strict'):
        return Codec.encode(input, errors, self.mapping)


class StreamReader(Codec, codecs.StreamReader):

    def __init__(self, stream, errors='strict', mapping=None):
        codecs.StreamReader.__init__(self, stream, errors)
        self.mapping = mapping

    def decode(self, input, errors='strict'):
        return Codec.decode(input, errors, self.mapping)


def getregentry():
    return codecs.CodecInfo(name='charmap',
      encode=(Codec.encode),
      decode=(Codec.decode),
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader)