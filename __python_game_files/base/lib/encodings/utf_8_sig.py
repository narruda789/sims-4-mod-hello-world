# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\utf_8_sig.py
# Compiled at: 2011-04-08 23:53:23
# Size of source mod 2**32: 4263 bytes
import codecs

def encode(input, errors='strict'):
    return (
     codecs.BOM_UTF8 + codecs.utf_8_encode(input, errors)[0],
     len(input))


def decode(input, errors='strict'):
    prefix = 0
    if input[:3] == codecs.BOM_UTF8:
        input = input[3:]
        prefix = 3
    output, consumed = codecs.utf_8_decode(input, errors, True)
    return (output, consumed + prefix)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.first = 1

    def encode(self, input, final=False):
        if self.first:
            self.first = 0
            return codecs.BOM_UTF8 + codecs.utf_8_encode(input, self.errors)[0]
        return codecs.utf_8_encode(input, self.errors)[0]

    def reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.first = 1

    def getstate(self):
        return self.first

    def setstate(self, state):
        self.first = state


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):

    def __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.first = 1

    def _buffer_decode(self, input, errors, final):
        if self.first:
            if len(input) < 3:
                if codecs.BOM_UTF8.startswith(input):
                    return ('', 0)
                self.first = 0
            else:
                self.first = 0
                if input[:3] == codecs.BOM_UTF8:
                    output, consumed = codecs.utf_8_decode(input[3:], errors, final)
                    return (output, consumed + 3)
        return codecs.utf_8_decode(input, errors, final)

    def reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.first = 1

    def getstate(self):
        state = codecs.BufferedIncrementalDecoder.getstate(self)
        return (
         state[0], self.first)

    def setstate(self, state):
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        self.first = state[1]


class StreamWriter(codecs.StreamWriter):

    def reset(self):
        codecs.StreamWriter.reset(self)
        try:
            del self.encode
        except AttributeError:
            pass

    def encode(self, input, errors='strict'):
        self.encode = codecs.utf_8_encode
        return encode(input, errors)


class StreamReader(codecs.StreamReader):

    def reset(self):
        codecs.StreamReader.reset(self)
        try:
            del self.decode
        except AttributeError:
            pass

    def decode(self, input, errors='strict'):
        if len(input) < 3:
            if codecs.BOM_UTF8.startswith(input):
                return ('', 0)
        elif input[:3] == codecs.BOM_UTF8:
            self.decode = codecs.utf_8_decode
            output, consumed = codecs.utf_8_decode(input[3:], errors)
            return (output, consumed + 3)
        self.decode = codecs.utf_8_decode
        return codecs.utf_8_decode(input, errors)


def getregentry():
    return codecs.CodecInfo(name='utf-8-sig',
      encode=encode,
      decode=decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)