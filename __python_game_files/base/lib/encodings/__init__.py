# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5838 bytes
import codecs, sys
from . import aliases
_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_aliases = aliases.aliases

class CodecRegistryError(LookupError, SystemError):
    pass


def normalize_encoding(encoding):
    if isinstance(encoding, bytes):
        encoding = str(encoding, 'ascii')
    chars = []
    punct = False
    for c in encoding:
        if not c.isalnum() or c == '.':
            if punct:
                if chars:
                    chars.append('_')
            chars.append(c)
            punct = False
        else:
            punct = True

    return ''.join(chars)


def search_function(encoding):
    entry = _cache.get(encoding, _unknown)
    if entry is not _unknown:
        return entry
    norm_encoding = normalize_encoding(encoding)
    aliased_encoding = _aliases.get(norm_encoding) or _aliases.get(norm_encoding.replace('.', '_'))
    if aliased_encoding is not None:
        modnames = [
         aliased_encoding,
         norm_encoding]
    else:
        modnames = [
         norm_encoding]
    for modname in modnames:
        if modname:
            if '.' in modname:
                continue
            try:
                mod = __import__(('encodings.' + modname), fromlist=_import_tail, level=0)
            except ImportError:
                pass
            else:
                break
    else:
        mod = None
    try:
        getregentry = mod.getregentry
    except AttributeError:
        mod = None

    if mod is None:
        _cache[encoding] = None
        return
    entry = getregentry()
    if not isinstance(entry, codecs.CodecInfo):
        if not 4<= len(entry) <= 7:
            raise CodecRegistryError('module "%s" (%s) failed to register' % (
             mod.__name__, mod.__file__))
        if not callable(entry[0])and callable(entry[1]) and callable(entry[1]) or callable(entry[2]):
            if not entry[3] is not None or callable(entry[3]):
                if len(entry) > 4:
                    if not entry[4] is not None or callable(entry[4]):
                        if len(entry) > 5:
                            if not (entry[5] is not None and callable(entry[5])):
                                raise CodecRegistryError('incompatible codecs in module "%s" (%s)' % (
                                 mod.__name__, mod.__file__))
                if len(entry) < 7 or entry[6] is None:
                    entry += (None, ) * (6 - len(entry)) + (mod.__name__.split('.', 1)[1],)
        entry = (codecs.CodecInfo)(*entry)
    _cache[encoding] = entry
    try:
        codecaliases = mod.getaliases()
    except AttributeError:
        pass
    else:
        for alias in codecaliases:
            if alias not in _aliases:
                _aliases[alias] = modname

    return entry


codecs.register(search_function)
if sys.platform == 'win32':

    def _alias_mbcs(encoding):
        try:
            import _winapi
            ansi_code_page = 'cp%s' % _winapi.GetACP()
            if encoding == ansi_code_page:
                import encodings.mbcs
                return encodings.mbcs.getregentry()
        except ImportError:
            pass


    codecs.register(_alias_mbcs)