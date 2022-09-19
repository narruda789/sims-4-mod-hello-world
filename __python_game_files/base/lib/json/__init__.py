# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\json\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 14451 bytes
__version__ = '2.0.9'
__all__ = [
 'dump', 'dumps', 'load', 'loads',
 'JSONDecoder', 'JSONDecodeError', 'JSONEncoder']
__author__ = 'Bob Ippolito <bob@redivi.com>'
from .decoder import JSONDecoder, JSONDecodeError
from .encoder import JSONEncoder
import codecs
_default_encoder = JSONEncoder(skipkeys=False,
  ensure_ascii=True,
  check_circular=True,
  allow_nan=True,
  indent=None,
  separators=None,
  default=None)

def dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw):
    if not skipkeys:
        if ensure_ascii and check_circular and allow_nan and cls is None and indent is None and separators is None and default is None and not sort_keys:
            if not kw:
                iterable = _default_encoder.iterencode(obj)
    else:
        if cls is None:
            cls = JSONEncoder
        iterable = cls(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, 
         allow_nan=allow_nan, indent=indent, separators=separators, 
         default=default, 
         sort_keys=sort_keys, **kw).iterencode(obj)
    for chunk in iterable:
        fp.write(chunk)


def dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw):
    if not skipkeys:
        if ensure_ascii:
            if check_circular:
                if allow_nan:
                    if cls is None:
                        if indent is None:
                            if separators is None:
                                if default is None:
                                    if not sort_keys:
                                        if not kw:
                                            return _default_encoder.encode(obj)
    if cls is None:
        cls = JSONEncoder
    return cls(skipkeys=skipkeys, 
     ensure_ascii=ensure_ascii, check_circular=check_circular, 
     allow_nan=allow_nan, indent=indent, separators=separators, 
     default=default, sort_keys=sort_keys, **kw).encode(obj)


_default_decoder = JSONDecoder(object_hook=None, object_pairs_hook=None)

def detect_encoding(b):
    bstartswith = b.startswith
    if bstartswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
        return 'utf-32'
        if bstartswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
            return 'utf-16'
        if bstartswith(codecs.BOM_UTF8):
            return 'utf-8-sig'
        if len(b) >= 4:
            if not b[0]:
                if b[1]:
                    return 'utf-16-be'
                return 'utf-32-be'
    elif not b[1]:
        if not b[2]:
            if b[3]:
                return 'utf-16-le'
            return 'utf-32-le'
        else:
            if len(b) == 2:
                if not b[0]:
                    return 'utf-16-be'
                if not b[1]:
                    return 'utf-16-le'
    return 'utf-8'


def load(fp, *, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
    return loads(fp.read(), cls=cls, 
     object_hook=object_hook, parse_float=parse_float, 
     parse_int=parse_int, parse_constant=parse_constant, 
     object_pairs_hook=object_pairs_hook, **kw)


def loads(s, *, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
    if isinstance(s, str):
        if s.startswith('\ufeff'):
            raise JSONDecodeError('Unexpected UTF-8 BOM (decode using utf-8-sig)', s, 0)
    else:
        if not isinstance(s, (bytes, bytearray)):
            raise TypeError(f"the JSON object must be str, bytes or bytearray, not {s.__class__.__name__}")
        s = s.decode(detect_encoding(s), 'surrogatepass')
    if cls is None:
        if object_hook is None:
            if parse_int is None:
                if parse_float is None:
                    if parse_constant is None:
                        if object_pairs_hook is None:
                            if not kw:
                                return _default_decoder.decode(s)
    if cls is None:
        cls = JSONDecoder
    if object_hook is not None:
        kw['object_hook'] = object_hook
    if object_pairs_hook is not None:
        kw['object_pairs_hook'] = object_pairs_hook
    if parse_float is not None:
        kw['parse_float'] = parse_float
    if parse_int is not None:
        kw['parse_int'] = parse_int
    if parse_constant is not None:
        kw['parse_constant'] = parse_constant
    return cls(**kw).decode(s)