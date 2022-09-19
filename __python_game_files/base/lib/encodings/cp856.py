# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\cp856.py
# Compiled at: 2011-04-08 23:53:23
# Size of source mod 2**32: 12730 bytes
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_table)

    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='cp856',
      encode=(Codec().encode),
      decode=(Codec().decode),
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)


decoding_table = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7fאבגדהוזחטיךכלםמןנסעףפץצקרשת\ufffe£\ufffe×\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe®¬½¼\ufffe«»░▒▓│┤\ufffe\ufffe\ufffe©╣║╗╝¢¥┐└┴┬├─┼\ufffe\ufffe╚╔╩╦╠═╬¤\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe┘┌█▄¦\ufffe▀\ufffe\ufffe\ufffe\ufffe\ufffe\ufffeµ\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe\ufffe¯´\xad±‗¾¶§÷¸°¨·¹³²■\xa0'
encoding_table = codecs.charmap_build(decoding_table)