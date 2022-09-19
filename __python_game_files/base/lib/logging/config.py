# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\logging\config.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 36729 bytes
import errno, io, logging, logging.handlers, re, struct, sys, threading, traceback
from socketserver import ThreadingTCPServer, StreamRequestHandler
DEFAULT_LOGGING_CONFIG_PORT = 9030
RESET_ERROR = errno.ECONNRESET
_listener = None

def fileConfig(fname, defaults=None, disable_existing_loggers=True):
    import configparser
    if isinstance(fname, configparser.RawConfigParser):
        cp = fname
    else:
        cp = configparser.ConfigParser(defaults)
        if hasattr(fname, 'readline'):
            cp.read_file(fname)
        else:
            cp.read(fname)
    formatters = _create_formatters(cp)
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()


def _resolve(name):
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found


def _strip_spaces(alist):
    return map(str.strip, alist)


def _create_formatters(cp):
    flist = cp['formatters']['keys']
    if not len(flist):
        return {}
    flist = flist.split(',')
    flist = _strip_spaces(flist)
    formatters = {}
    for form in flist:
        sectname = 'formatter_%s' % form
        fs = cp.get(sectname, 'format', raw=True, fallback=None)
        dfs = cp.get(sectname, 'datefmt', raw=True, fallback=None)
        stl = cp.get(sectname, 'style', raw=True, fallback='%')
        c = logging.Formatter
        class_name = cp[sectname].get('class')
        if class_name:
            c = _resolve(class_name)
        f = c(fs, dfs, stl)
        formatters[form] = f

    return formatters


def _install_handlers(cp, formatters):
    hlist = cp['handlers']['keys']
    if not len(hlist):
        return {}
    hlist = hlist.split(',')
    hlist = _strip_spaces(hlist)
    handlers = {}
    fixups = []
    for hand in hlist:
        section = cp[('handler_%s' % hand)]
        klass = section['class']
        fmt = section.get('formatter', '')
        try:
            klass = eval(klass, vars(logging))
        except (AttributeError, NameError):
            klass = _resolve(klass)

        args = section.get('args', '()')
        args = eval(args, vars(logging))
        kwargs = section.get('kwargs', '{}')
        kwargs = eval(kwargs, vars(logging))
        h = klass(*args, **kwargs)
        if 'level' in section:
            level = section['level']
            h.setLevel(level)
        if len(fmt):
            h.setFormatter(formatters[fmt])
        if issubclass(klass, logging.handlers.MemoryHandler):
            target = section.get('target', '')
            if len(target):
                fixups.append((h, target))
        handlers[hand] = h

    for h, t in fixups:
        h.setTarget(handlers[t])

    return handlers


def _handle_existing_loggers(existing, child_loggers, disable_existing):
    root = logging.root
    for log in existing:
        logger = root.manager.loggerDict[log]
        if log in child_loggers:
            logger.level = logging.NOTSET
            logger.handlers = []
            logger.propagate = True
        else:
            logger.disabled = disable_existing


def _install_loggers(cp, handlers, disable_existing):
    llist = cp['loggers']['keys']
    llist = llist.split(',')
    llist = list(_strip_spaces(llist))
    llist.remove('root')
    section = cp['logger_root']
    root = logging.root
    log = root
    if 'level' in section:
        level = section['level']
        log.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)

    hlist = section['handlers']
    if len(hlist):
        hlist = hlist.split(',')
        hlist = _strip_spaces(hlist)
        for hand in hlist:
            log.addHandler(handlers[hand])

    existing = list(root.manager.loggerDict.keys())
    existing.sort()
    child_loggers = []
    for log in llist:
        section = cp[('logger_%s' % log)]
        qn = section['qualname']
        propagate = section.getint('propagate', fallback=1)
        logger = logging.getLogger(qn)
        if qn in existing:
            i = existing.index(qn) + 1
            prefixed = qn + '.'
            pflen = len(prefixed)
            num_existing = len(existing)
            while i < num_existing:
                if existing[i][:pflen] == prefixed:
                    child_loggers.append(existing[i])
                i += 1

            existing.remove(qn)
        if 'level' in section:
            level = section['level']
            logger.setLevel(level)
        for h in logger.handlers[:]:
            logger.removeHandler(h)

        logger.propagate = propagate
        logger.disabled = 0
        hlist = section['handlers']
        if len(hlist):
            hlist = hlist.split(',')
            hlist = _strip_spaces(hlist)
            for hand in hlist:
                logger.addHandler(handlers[hand])

    _handle_existing_loggers(existing, child_loggers, disable_existing)


IDENTIFIER = re.compile('^[a-z_][a-z0-9_]*$', re.I)

def valid_ident(s):
    m = IDENTIFIER.match(s)
    if not m:
        raise ValueError('Not a valid Python identifier: %r' % s)
    return True


class ConvertingMixin(object):

    def convert_with_key(self, key, value, replace=True):
        result = self.configurator.convert(value)
        if value is not result:
            if replace:
                self[key] = result
            if type(result) in (ConvertingDict, ConvertingList,
             ConvertingTuple):
                result.parent = self
                result.key = key
        return result

    def convert(self, value):
        result = self.configurator.convert(value)
        if value is not result:
            if type(result) in (ConvertingDict, ConvertingList,
             ConvertingTuple):
                result.parent = self
        return result


class ConvertingDict(dict, ConvertingMixin):

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        return self.convert_with_key(key, value)

    def get(self, key, default=None):
        value = dict.get(self, key, default)
        return self.convert_with_key(key, value)

    def pop(self, key, default=None):
        value = dict.pop(self, key, default)
        return self.convert_with_key(key, value, replace=False)


class ConvertingList(list, ConvertingMixin):

    def __getitem__(self, key):
        value = list.__getitem__(self, key)
        return self.convert_with_key(key, value)

    def pop(self, idx=-1):
        value = list.pop(self, idx)
        return self.convert(value)


class ConvertingTuple(tuple, ConvertingMixin):

    def __getitem__(self, key):
        value = tuple.__getitem__(self, key)
        return self.convert_with_key(key, value, replace=False)


class BaseConfigurator(object):
    CONVERT_PATTERN = re.compile('^(?P<prefix>[a-z]+)://(?P<suffix>.*)$')
    WORD_PATTERN = re.compile('^\\s*(\\w+)\\s*')
    DOT_PATTERN = re.compile('^\\.\\s*(\\w+)\\s*')
    INDEX_PATTERN = re.compile('^\\[\\s*(\\w+)\\s*\\]\\s*')
    DIGIT_PATTERN = re.compile('^\\d+$')
    value_converters = {'ext':'ext_convert', 
     'cfg':'cfg_convert'}
    importer = staticmethod(__import__)

    def __init__(self, config):
        self.config = ConvertingDict(config)
        self.config.configurator = self

    def resolve(self, s):
        name = s.split('.')
        used = name.pop(0)
        try:
            found = self.importer(used)
            for frag in name:
                used += '.' + frag
                try:
                    found = getattr(found, frag)
                except AttributeError:
                    self.importer(used)
                    found = getattr(found, frag)

            return found
        except ImportError:
            e, tb = sys.exc_info()[1:]
            v = ValueError('Cannot resolve %r: %s' % (s, e))
            v.__cause__, v.__traceback__ = e, tb
            raise v

    def ext_convert(self, value):
        return self.resolve(value)

    def cfg_convert(self, value):
        rest = value
        m = self.WORD_PATTERN.match(rest)
        if m is None:
            raise ValueError('Unable to convert %r' % value)
        else:
            rest = rest[m.end():]
            d = self.config[m.groups()[0]]
            while rest:
                m = self.DOT_PATTERN.match(rest)
                if m:
                    d = d[m.groups()[0]]
                else:
                    m = self.INDEX_PATTERN.match(rest)
                if m:
                    idx = m.groups()[0]
                    if not self.DIGIT_PATTERN.match(idx):
                        d = d[idx]
                    else:
                        try:
                            n = int(idx)
                            d = d[n]
                        except TypeError:
                            d = d[idx]

                    if m:
                        rest = rest[m.end():]
                else:
                    raise ValueError('Unable to convert %r at %r' % (
                     value, rest))

        return d

    def convert(self, value):
        if (isinstance(value, ConvertingDict) or isinstance)(value, dict):
            value = ConvertingDict(value)
            value.configurator = self
        else:
            if (isinstance(value, ConvertingList) or isinstance)(value, list):
                value = ConvertingList(value)
                value.configurator = self
            else:
                if (isinstance(value, ConvertingTuple) or isinstance)(value, tuple):
                    value = ConvertingTuple(value)
                    value.configurator = self
                else:
                    if isinstance(value, str):
                        m = self.CONVERT_PATTERN.match(value)
                        if m:
                            d = m.groupdict()
                            prefix = d['prefix']
                            converter = self.value_converters.get(prefix, None)
                            if converter:
                                suffix = d['suffix']
                                converter = getattr(self, converter)
                                value = converter(suffix)
        return value

    def configure_custom(self, config):
        c = config.pop('()')
        if not callable(c):
            c = self.resolve(c)
        props = config.pop('.', None)
        kwargs = {k:config[k] for k in config if valid_ident(k)}
        result = c(**kwargs)
        if props:
            for name, value in props.items():
                setattr(result, name, value)

        return result

    def as_tuple(self, value):
        if isinstance(value, list):
            value = tuple(value)
        return value


class DictConfigurator(BaseConfigurator):

    def configure--- This code section failed: ---

 L. 485         0  LOAD_FAST                'self'
                2  LOAD_ATTR                config
                4  STORE_FAST               'config'

 L. 486         6  LOAD_STR                 'version'
                8  LOAD_FAST                'config'
               10  COMPARE_OP               not-in
               12  POP_JUMP_IF_FALSE    22  'to 22'

 L. 487        14  LOAD_GLOBAL              ValueError
               16  LOAD_STR                 "dictionary doesn't specify a version"
               18  CALL_FUNCTION_1       1  '1 positional argument'
               20  RAISE_VARARGS_1       1  'exception instance'
             22_0  COME_FROM            12  '12'

 L. 488        22  LOAD_FAST                'config'
               24  LOAD_STR                 'version'
               26  BINARY_SUBSCR    
               28  LOAD_CONST               1
               30  COMPARE_OP               !=
               32  POP_JUMP_IF_FALSE    50  'to 50'

 L. 489        34  LOAD_GLOBAL              ValueError
               36  LOAD_STR                 'Unsupported version: %s'
               38  LOAD_FAST                'config'
               40  LOAD_STR                 'version'
               42  BINARY_SUBSCR    
               44  BINARY_MODULO    
               46  CALL_FUNCTION_1       1  '1 positional argument'
               48  RAISE_VARARGS_1       1  'exception instance'
             50_0  COME_FROM            32  '32'

 L. 490        50  LOAD_FAST                'config'
               52  LOAD_METHOD              pop
               54  LOAD_STR                 'incremental'
               56  LOAD_CONST               False
               58  CALL_METHOD_2         2  '2 positional arguments'
               60  STORE_FAST               'incremental'

 L. 491        62  BUILD_MAP_0           0 
               64  STORE_FAST               'EMPTY_DICT'

 L. 492        66  LOAD_GLOBAL              logging
               68  LOAD_METHOD              _acquireLock
               70  CALL_METHOD_0         0  '0 positional arguments'
               72  POP_TOP          

 L. 493     74_76  SETUP_FINALLY      1262  'to 1262'

 L. 494        78  LOAD_FAST                'incremental'
            80_82  POP_JUMP_IF_FALSE   426  'to 426'

 L. 495        84  LOAD_FAST                'config'
               86  LOAD_METHOD              get
               88  LOAD_STR                 'handlers'
               90  LOAD_FAST                'EMPTY_DICT'
               92  CALL_METHOD_2         2  '2 positional arguments'
               94  STORE_FAST               'handlers'

 L. 496        96  SETUP_LOOP          238  'to 238'
               98  LOAD_FAST                'handlers'
              100  GET_ITER         
              102  FOR_ITER            236  'to 236'
              104  STORE_FAST               'name'

 L. 497       106  LOAD_FAST                'name'
              108  LOAD_GLOBAL              logging
              110  LOAD_ATTR                _handlers
              112  COMPARE_OP               not-in
              114  POP_JUMP_IF_FALSE   130  'to 130'

 L. 498       116  LOAD_GLOBAL              ValueError
              118  LOAD_STR                 'No handler found with name %r'

 L. 499       120  LOAD_FAST                'name'
              122  BINARY_MODULO    
              124  CALL_FUNCTION_1       1  '1 positional argument'
              126  RAISE_VARARGS_1       1  'exception instance'
              128  JUMP_BACK           102  'to 102'
            130_0  COME_FROM           114  '114'

 L. 501       130  SETUP_EXCEPT        186  'to 186'

 L. 502       132  LOAD_GLOBAL              logging
              134  LOAD_ATTR                _handlers
              136  LOAD_FAST                'name'
              138  BINARY_SUBSCR    
              140  STORE_FAST               'handler'

 L. 503       142  LOAD_FAST                'handlers'
              144  LOAD_FAST                'name'
              146  BINARY_SUBSCR    
              148  STORE_FAST               'handler_config'

 L. 504       150  LOAD_FAST                'handler_config'
              152  LOAD_METHOD              get
              154  LOAD_STR                 'level'
              156  LOAD_CONST               None
              158  CALL_METHOD_2         2  '2 positional arguments'
              160  STORE_FAST               'level'

 L. 505       162  LOAD_FAST                'level'
              164  POP_JUMP_IF_FALSE   182  'to 182'

 L. 506       166  LOAD_FAST                'handler'
              168  LOAD_METHOD              setLevel
              170  LOAD_GLOBAL              logging
              172  LOAD_METHOD              _checkLevel
              174  LOAD_FAST                'level'
              176  CALL_METHOD_1         1  '1 positional argument'
              178  CALL_METHOD_1         1  '1 positional argument'
              180  POP_TOP          
            182_0  COME_FROM           164  '164'
              182  POP_BLOCK        
              184  JUMP_BACK           102  'to 102'
            186_0  COME_FROM_EXCEPT    130  '130'

 L. 507       186  DUP_TOP          
              188  LOAD_GLOBAL              Exception
              190  COMPARE_OP               exception-match
              192  POP_JUMP_IF_FALSE   232  'to 232'
              194  POP_TOP          
              196  STORE_FAST               'e'
              198  POP_TOP          
              200  SETUP_FINALLY       220  'to 220'

 L. 508       202  LOAD_GLOBAL              ValueError
              204  LOAD_STR                 'Unable to configure handler %r'

 L. 509       206  LOAD_FAST                'name'
              208  BINARY_MODULO    
              210  CALL_FUNCTION_1       1  '1 positional argument'
              212  LOAD_FAST                'e'
              214  RAISE_VARARGS_2       2  'exception instance with __cause__'
              216  POP_BLOCK        
              218  LOAD_CONST               None
            220_0  COME_FROM_FINALLY   200  '200'
              220  LOAD_CONST               None
              222  STORE_FAST               'e'
              224  DELETE_FAST              'e'
              226  END_FINALLY      
              228  POP_EXCEPT       
              230  JUMP_BACK           102  'to 102'
            232_0  COME_FROM           192  '192'
              232  END_FINALLY      
              234  JUMP_BACK           102  'to 102'
              236  POP_BLOCK        
            238_0  COME_FROM_LOOP       96  '96'

 L. 510       238  LOAD_FAST                'config'
              240  LOAD_METHOD              get
              242  LOAD_STR                 'loggers'
              244  LOAD_FAST                'EMPTY_DICT'
              246  CALL_METHOD_2         2  '2 positional arguments'
              248  STORE_FAST               'loggers'

 L. 511       250  SETUP_LOOP          340  'to 340'
              252  LOAD_FAST                'loggers'
              254  GET_ITER         
              256  FOR_ITER            338  'to 338'
              258  STORE_FAST               'name'

 L. 512       260  SETUP_EXCEPT        284  'to 284'

 L. 513       262  LOAD_FAST                'self'
              264  LOAD_METHOD              configure_logger
              266  LOAD_FAST                'name'
              268  LOAD_FAST                'loggers'
              270  LOAD_FAST                'name'
              272  BINARY_SUBSCR    
              274  LOAD_CONST               True
              276  CALL_METHOD_3         3  '3 positional arguments'
              278  POP_TOP          
              280  POP_BLOCK        
              282  JUMP_BACK           256  'to 256'
            284_0  COME_FROM_EXCEPT    260  '260'

 L. 514       284  DUP_TOP          
              286  LOAD_GLOBAL              Exception
              288  COMPARE_OP               exception-match
          290_292  POP_JUMP_IF_FALSE   332  'to 332'
              294  POP_TOP          
              296  STORE_FAST               'e'
              298  POP_TOP          
              300  SETUP_FINALLY       320  'to 320'

 L. 515       302  LOAD_GLOBAL              ValueError
              304  LOAD_STR                 'Unable to configure logger %r'

 L. 516       306  LOAD_FAST                'name'
              308  BINARY_MODULO    
              310  CALL_FUNCTION_1       1  '1 positional argument'
              312  LOAD_FAST                'e'
              314  RAISE_VARARGS_2       2  'exception instance with __cause__'
              316  POP_BLOCK        
              318  LOAD_CONST               None
            320_0  COME_FROM_FINALLY   300  '300'
              320  LOAD_CONST               None
              322  STORE_FAST               'e'
              324  DELETE_FAST              'e'
              326  END_FINALLY      
              328  POP_EXCEPT       
              330  JUMP_BACK           256  'to 256'
            332_0  COME_FROM           290  '290'
              332  END_FINALLY      
          334_336  JUMP_BACK           256  'to 256'
              338  POP_BLOCK        
            340_0  COME_FROM_LOOP      250  '250'

 L. 517       340  LOAD_FAST                'config'
              342  LOAD_METHOD              get
              344  LOAD_STR                 'root'
              346  LOAD_CONST               None
              348  CALL_METHOD_2         2  '2 positional arguments'
              350  STORE_FAST               'root'

 L. 518       352  LOAD_FAST                'root'
          354_356  POP_JUMP_IF_FALSE  1258  'to 1258'

 L. 519       358  SETUP_EXCEPT        376  'to 376'

 L. 520       360  LOAD_FAST                'self'
              362  LOAD_METHOD              configure_root
              364  LOAD_FAST                'root'
              366  LOAD_CONST               True
              368  CALL_METHOD_2         2  '2 positional arguments'
              370  POP_TOP          
              372  POP_BLOCK        
              374  JUMP_FORWARD       1258  'to 1258'
            376_0  COME_FROM_EXCEPT    358  '358'

 L. 521       376  DUP_TOP          
              378  LOAD_GLOBAL              Exception
              380  COMPARE_OP               exception-match
          382_384  POP_JUMP_IF_FALSE   420  'to 420'
              386  POP_TOP          
              388  STORE_FAST               'e'
              390  POP_TOP          
              392  SETUP_FINALLY       408  'to 408'

 L. 522       394  LOAD_GLOBAL              ValueError
              396  LOAD_STR                 'Unable to configure root logger'
              398  CALL_FUNCTION_1       1  '1 positional argument'

 L. 523       400  LOAD_FAST                'e'
              402  RAISE_VARARGS_2       2  'exception instance with __cause__'
              404  POP_BLOCK        
              406  LOAD_CONST               None
            408_0  COME_FROM_FINALLY   392  '392'
              408  LOAD_CONST               None
              410  STORE_FAST               'e'
              412  DELETE_FAST              'e'
              414  END_FINALLY      
              416  POP_EXCEPT       
              418  JUMP_FORWARD       1258  'to 1258'
            420_0  COME_FROM           382  '382'
              420  END_FINALLY      
          422_424  JUMP_FORWARD       1258  'to 1258'
            426_0  COME_FROM            80  '80'

 L. 525       426  LOAD_FAST                'config'
              428  LOAD_METHOD              pop
              430  LOAD_STR                 'disable_existing_loggers'
              432  LOAD_CONST               True
              434  CALL_METHOD_2         2  '2 positional arguments'
              436  STORE_FAST               'disable_existing'

 L. 527       438  LOAD_GLOBAL              logging
              440  LOAD_ATTR                _handlers
              442  LOAD_METHOD              clear
              444  CALL_METHOD_0         0  '0 positional arguments'
              446  POP_TOP          

 L. 528       448  LOAD_GLOBAL              logging
              450  LOAD_ATTR                _handlerList
              452  LOAD_CONST               None
              454  LOAD_CONST               None
              456  BUILD_SLICE_2         2 
              458  DELETE_SUBSCR    

 L. 531       460  LOAD_FAST                'config'
              462  LOAD_METHOD              get
              464  LOAD_STR                 'formatters'
              466  LOAD_FAST                'EMPTY_DICT'
              468  CALL_METHOD_2         2  '2 positional arguments'
              470  STORE_FAST               'formatters'

 L. 532       472  SETUP_LOOP          562  'to 562'
              474  LOAD_FAST                'formatters'
              476  GET_ITER         
              478  FOR_ITER            560  'to 560'
              480  STORE_FAST               'name'

 L. 533       482  SETUP_EXCEPT        506  'to 506'

 L. 534       484  LOAD_FAST                'self'
              486  LOAD_METHOD              configure_formatter

 L. 535       488  LOAD_FAST                'formatters'
              490  LOAD_FAST                'name'
              492  BINARY_SUBSCR    
              494  CALL_METHOD_1         1  '1 positional argument'
              496  LOAD_FAST                'formatters'
              498  LOAD_FAST                'name'
              500  STORE_SUBSCR     
              502  POP_BLOCK        
              504  JUMP_BACK           478  'to 478'
            506_0  COME_FROM_EXCEPT    482  '482'

 L. 536       506  DUP_TOP          
              508  LOAD_GLOBAL              Exception
              510  COMPARE_OP               exception-match
          512_514  POP_JUMP_IF_FALSE   554  'to 554'
              516  POP_TOP          
              518  STORE_FAST               'e'
              520  POP_TOP          
              522  SETUP_FINALLY       542  'to 542'

 L. 537       524  LOAD_GLOBAL              ValueError
              526  LOAD_STR                 'Unable to configure formatter %r'

 L. 538       528  LOAD_FAST                'name'
              530  BINARY_MODULO    
              532  CALL_FUNCTION_1       1  '1 positional argument'
              534  LOAD_FAST                'e'
              536  RAISE_VARARGS_2       2  'exception instance with __cause__'
              538  POP_BLOCK        
              540  LOAD_CONST               None
            542_0  COME_FROM_FINALLY   522  '522'
              542  LOAD_CONST               None
              544  STORE_FAST               'e'
              546  DELETE_FAST              'e'
              548  END_FINALLY      
              550  POP_EXCEPT       
              552  JUMP_BACK           478  'to 478'
            554_0  COME_FROM           512  '512'
              554  END_FINALLY      
          556_558  JUMP_BACK           478  'to 478'
              560  POP_BLOCK        
            562_0  COME_FROM_LOOP      472  '472'

 L. 540       562  LOAD_FAST                'config'
              564  LOAD_METHOD              get
              566  LOAD_STR                 'filters'
              568  LOAD_FAST                'EMPTY_DICT'
              570  CALL_METHOD_2         2  '2 positional arguments'
              572  STORE_FAST               'filters'

 L. 541       574  SETUP_LOOP          664  'to 664'
              576  LOAD_FAST                'filters'
              578  GET_ITER         
              580  FOR_ITER            662  'to 662'
              582  STORE_FAST               'name'

 L. 542       584  SETUP_EXCEPT        608  'to 608'

 L. 543       586  LOAD_FAST                'self'
              588  LOAD_METHOD              configure_filter
              590  LOAD_FAST                'filters'
              592  LOAD_FAST                'name'
              594  BINARY_SUBSCR    
              596  CALL_METHOD_1         1  '1 positional argument'
              598  LOAD_FAST                'filters'
              600  LOAD_FAST                'name'
              602  STORE_SUBSCR     
              604  POP_BLOCK        
              606  JUMP_BACK           580  'to 580'
            608_0  COME_FROM_EXCEPT    584  '584'

 L. 544       608  DUP_TOP          
              610  LOAD_GLOBAL              Exception
              612  COMPARE_OP               exception-match
          614_616  POP_JUMP_IF_FALSE   656  'to 656'
              618  POP_TOP          
              620  STORE_FAST               'e'
              622  POP_TOP          
              624  SETUP_FINALLY       644  'to 644'

 L. 545       626  LOAD_GLOBAL              ValueError
              628  LOAD_STR                 'Unable to configure filter %r'

 L. 546       630  LOAD_FAST                'name'
              632  BINARY_MODULO    
              634  CALL_FUNCTION_1       1  '1 positional argument'
              636  LOAD_FAST                'e'
              638  RAISE_VARARGS_2       2  'exception instance with __cause__'
              640  POP_BLOCK        
              642  LOAD_CONST               None
            644_0  COME_FROM_FINALLY   624  '624'
              644  LOAD_CONST               None
              646  STORE_FAST               'e'
              648  DELETE_FAST              'e'
              650  END_FINALLY      
              652  POP_EXCEPT       
              654  JUMP_BACK           580  'to 580'
            656_0  COME_FROM           614  '614'
              656  END_FINALLY      
          658_660  JUMP_BACK           580  'to 580'
              662  POP_BLOCK        
            664_0  COME_FROM_LOOP      574  '574'

 L. 551       664  LOAD_FAST                'config'
              666  LOAD_METHOD              get
              668  LOAD_STR                 'handlers'
              670  LOAD_FAST                'EMPTY_DICT'
              672  CALL_METHOD_2         2  '2 positional arguments'
              674  STORE_FAST               'handlers'

 L. 552       676  BUILD_LIST_0          0 
              678  STORE_FAST               'deferred'

 L. 553       680  SETUP_LOOP          812  'to 812'
              682  LOAD_GLOBAL              sorted
              684  LOAD_FAST                'handlers'
              686  CALL_FUNCTION_1       1  '1 positional argument'
              688  GET_ITER         
              690  FOR_ITER            810  'to 810'
              692  STORE_FAST               'name'

 L. 554       694  SETUP_EXCEPT        728  'to 728'

 L. 555       696  LOAD_FAST                'self'
              698  LOAD_METHOD              configure_handler
              700  LOAD_FAST                'handlers'
              702  LOAD_FAST                'name'
              704  BINARY_SUBSCR    
              706  CALL_METHOD_1         1  '1 positional argument'
              708  STORE_FAST               'handler'

 L. 556       710  LOAD_FAST                'name'
              712  LOAD_FAST                'handler'
              714  STORE_ATTR               name

 L. 557       716  LOAD_FAST                'handler'
              718  LOAD_FAST                'handlers'
              720  LOAD_FAST                'name'
              722  STORE_SUBSCR     
              724  POP_BLOCK        
              726  JUMP_BACK           690  'to 690'
            728_0  COME_FROM_EXCEPT    694  '694'

 L. 558       728  DUP_TOP          
              730  LOAD_GLOBAL              Exception
              732  COMPARE_OP               exception-match
          734_736  POP_JUMP_IF_FALSE   804  'to 804'
              738  POP_TOP          
              740  STORE_FAST               'e'
              742  POP_TOP          
              744  SETUP_FINALLY       792  'to 792'

 L. 559       746  LOAD_STR                 'target not configured yet'
              748  LOAD_GLOBAL              str
              750  LOAD_FAST                'e'
              752  LOAD_ATTR                __cause__
              754  CALL_FUNCTION_1       1  '1 positional argument'
              756  COMPARE_OP               in
          758_760  POP_JUMP_IF_FALSE   774  'to 774'

 L. 560       762  LOAD_FAST                'deferred'
              764  LOAD_METHOD              append
              766  LOAD_FAST                'name'
              768  CALL_METHOD_1         1  '1 positional argument'
              770  POP_TOP          
              772  JUMP_FORWARD        788  'to 788'
            774_0  COME_FROM           758  '758'

 L. 562       774  LOAD_GLOBAL              ValueError
              776  LOAD_STR                 'Unable to configure handler %r'

 L. 563       778  LOAD_FAST                'name'
              780  BINARY_MODULO    
              782  CALL_FUNCTION_1       1  '1 positional argument'
              784  LOAD_FAST                'e'
              786  RAISE_VARARGS_2       2  'exception instance with __cause__'
            788_0  COME_FROM           772  '772'
              788  POP_BLOCK        
              790  LOAD_CONST               None
            792_0  COME_FROM_FINALLY   744  '744'
              792  LOAD_CONST               None
              794  STORE_FAST               'e'
              796  DELETE_FAST              'e'
              798  END_FINALLY      
              800  POP_EXCEPT       
              802  JUMP_BACK           690  'to 690'
            804_0  COME_FROM           734  '734'
              804  END_FINALLY      
          806_808  JUMP_BACK           690  'to 690'
              810  POP_BLOCK        
            812_0  COME_FROM_LOOP      680  '680'

 L. 566       812  SETUP_LOOP          912  'to 912'
              814  LOAD_FAST                'deferred'
              816  GET_ITER         
              818  FOR_ITER            910  'to 910'
              820  STORE_FAST               'name'

 L. 567       822  SETUP_EXCEPT        856  'to 856'

 L. 568       824  LOAD_FAST                'self'
              826  LOAD_METHOD              configure_handler
              828  LOAD_FAST                'handlers'
              830  LOAD_FAST                'name'
              832  BINARY_SUBSCR    
              834  CALL_METHOD_1         1  '1 positional argument'
              836  STORE_FAST               'handler'

 L. 569       838  LOAD_FAST                'name'
              840  LOAD_FAST                'handler'
              842  STORE_ATTR               name

 L. 570       844  LOAD_FAST                'handler'
              846  LOAD_FAST                'handlers'
              848  LOAD_FAST                'name'
              850  STORE_SUBSCR     
              852  POP_BLOCK        
              854  JUMP_BACK           818  'to 818'
            856_0  COME_FROM_EXCEPT    822  '822'

 L. 571       856  DUP_TOP          
              858  LOAD_GLOBAL              Exception
              860  COMPARE_OP               exception-match
          862_864  POP_JUMP_IF_FALSE   904  'to 904'
              866  POP_TOP          
              868  STORE_FAST               'e'
              870  POP_TOP          
              872  SETUP_FINALLY       892  'to 892'

 L. 572       874  LOAD_GLOBAL              ValueError
              876  LOAD_STR                 'Unable to configure handler %r'

 L. 573       878  LOAD_FAST                'name'
              880  BINARY_MODULO    
              882  CALL_FUNCTION_1       1  '1 positional argument'
              884  LOAD_FAST                'e'
              886  RAISE_VARARGS_2       2  'exception instance with __cause__'
              888  POP_BLOCK        
              890  LOAD_CONST               None
            892_0  COME_FROM_FINALLY   872  '872'
              892  LOAD_CONST               None
              894  STORE_FAST               'e'
              896  DELETE_FAST              'e'
              898  END_FINALLY      
              900  POP_EXCEPT       
              902  JUMP_BACK           818  'to 818'
            904_0  COME_FROM           862  '862'
              904  END_FINALLY      
          906_908  JUMP_BACK           818  'to 818'
              910  POP_BLOCK        
            912_0  COME_FROM_LOOP      812  '812'

 L. 585       912  LOAD_GLOBAL              logging
              914  LOAD_ATTR                root
              916  STORE_FAST               'root'

 L. 586       918  LOAD_GLOBAL              list
              920  LOAD_FAST                'root'
              922  LOAD_ATTR                manager
              924  LOAD_ATTR                loggerDict
              926  LOAD_METHOD              keys
              928  CALL_METHOD_0         0  '0 positional arguments'
              930  CALL_FUNCTION_1       1  '1 positional argument'
              932  STORE_FAST               'existing'

 L. 591       934  LOAD_FAST                'existing'
              936  LOAD_METHOD              sort
              938  CALL_METHOD_0         0  '0 positional arguments'
              940  POP_TOP          

 L. 594       942  BUILD_LIST_0          0 
              944  STORE_FAST               'child_loggers'

 L. 596       946  LOAD_FAST                'config'
              948  LOAD_METHOD              get
              950  LOAD_STR                 'loggers'
              952  LOAD_FAST                'EMPTY_DICT'
              954  CALL_METHOD_2         2  '2 positional arguments'
              956  STORE_FAST               'loggers'

 L. 597       958  SETUP_LOOP         1166  'to 1166'
              960  LOAD_FAST                'loggers'
              962  GET_ITER         
              964  FOR_ITER           1164  'to 1164'
              966  STORE_FAST               'name'

 L. 598       968  LOAD_FAST                'name'
              970  LOAD_FAST                'existing'
              972  COMPARE_OP               in
          974_976  POP_JUMP_IF_FALSE  1088  'to 1088'

 L. 599       978  LOAD_FAST                'existing'
              980  LOAD_METHOD              index
              982  LOAD_FAST                'name'
              984  CALL_METHOD_1         1  '1 positional argument'
              986  LOAD_CONST               1
              988  BINARY_ADD       
              990  STORE_FAST               'i'

 L. 600       992  LOAD_FAST                'name'
              994  LOAD_STR                 '.'
              996  BINARY_ADD       
              998  STORE_FAST               'prefixed'

 L. 601      1000  LOAD_GLOBAL              len
             1002  LOAD_FAST                'prefixed'
             1004  CALL_FUNCTION_1       1  '1 positional argument'
             1006  STORE_FAST               'pflen'

 L. 602      1008  LOAD_GLOBAL              len
             1010  LOAD_FAST                'existing'
             1012  CALL_FUNCTION_1       1  '1 positional argument'
             1014  STORE_FAST               'num_existing'

 L. 603      1016  SETUP_LOOP         1078  'to 1078'
             1018  LOAD_FAST                'i'
             1020  LOAD_FAST                'num_existing'
             1022  COMPARE_OP               <
         1024_1026  POP_JUMP_IF_FALSE  1076  'to 1076'

 L. 604      1028  LOAD_FAST                'existing'
             1030  LOAD_FAST                'i'
             1032  BINARY_SUBSCR    
             1034  LOAD_CONST               None
             1036  LOAD_FAST                'pflen'
             1038  BUILD_SLICE_2         2 
             1040  BINARY_SUBSCR    
             1042  LOAD_FAST                'prefixed'
             1044  COMPARE_OP               ==
         1046_1048  POP_JUMP_IF_FALSE  1064  'to 1064'

 L. 605      1050  LOAD_FAST                'child_loggers'
             1052  LOAD_METHOD              append
             1054  LOAD_FAST                'existing'
             1056  LOAD_FAST                'i'
             1058  BINARY_SUBSCR    
             1060  CALL_METHOD_1         1  '1 positional argument'
             1062  POP_TOP          
           1064_0  COME_FROM          1046  '1046'

 L. 606      1064  LOAD_FAST                'i'
             1066  LOAD_CONST               1
             1068  INPLACE_ADD      
             1070  STORE_FAST               'i'
         1072_1074  JUMP_BACK          1018  'to 1018'
           1076_0  COME_FROM          1024  '1024'
             1076  POP_BLOCK        
           1078_0  COME_FROM_LOOP     1016  '1016'

 L. 607      1078  LOAD_FAST                'existing'
             1080  LOAD_METHOD              remove
             1082  LOAD_FAST                'name'
             1084  CALL_METHOD_1         1  '1 positional argument'
             1086  POP_TOP          
           1088_0  COME_FROM           974  '974'

 L. 608      1088  SETUP_EXCEPT       1110  'to 1110'

 L. 609      1090  LOAD_FAST                'self'
             1092  LOAD_METHOD              configure_logger
             1094  LOAD_FAST                'name'
             1096  LOAD_FAST                'loggers'
             1098  LOAD_FAST                'name'
             1100  BINARY_SUBSCR    
             1102  CALL_METHOD_2         2  '2 positional arguments'
             1104  POP_TOP          
             1106  POP_BLOCK        
             1108  JUMP_BACK           964  'to 964'
           1110_0  COME_FROM_EXCEPT   1088  '1088'

 L. 610      1110  DUP_TOP          
             1112  LOAD_GLOBAL              Exception
             1114  COMPARE_OP               exception-match
         1116_1118  POP_JUMP_IF_FALSE  1158  'to 1158'
             1120  POP_TOP          
             1122  STORE_FAST               'e'
             1124  POP_TOP          
             1126  SETUP_FINALLY      1146  'to 1146'

 L. 611      1128  LOAD_GLOBAL              ValueError
             1130  LOAD_STR                 'Unable to configure logger %r'

 L. 612      1132  LOAD_FAST                'name'
             1134  BINARY_MODULO    
             1136  CALL_FUNCTION_1       1  '1 positional argument'
             1138  LOAD_FAST                'e'
             1140  RAISE_VARARGS_2       2  'exception instance with __cause__'
             1142  POP_BLOCK        
             1144  LOAD_CONST               None
           1146_0  COME_FROM_FINALLY  1126  '1126'
             1146  LOAD_CONST               None
             1148  STORE_FAST               'e'
             1150  DELETE_FAST              'e'
             1152  END_FINALLY      
             1154  POP_EXCEPT       
             1156  JUMP_BACK           964  'to 964'
           1158_0  COME_FROM          1116  '1116'
             1158  END_FINALLY      
         1160_1162  JUMP_BACK           964  'to 964'
             1164  POP_BLOCK        
           1166_0  COME_FROM_LOOP      958  '958'

 L. 627      1166  LOAD_GLOBAL              _handle_existing_loggers
             1168  LOAD_FAST                'existing'
             1170  LOAD_FAST                'child_loggers'

 L. 628      1172  LOAD_FAST                'disable_existing'
             1174  CALL_FUNCTION_3       3  '3 positional arguments'
             1176  POP_TOP          

 L. 631      1178  LOAD_FAST                'config'
             1180  LOAD_METHOD              get
             1182  LOAD_STR                 'root'
             1184  LOAD_CONST               None
             1186  CALL_METHOD_2         2  '2 positional arguments'
             1188  STORE_FAST               'root'

 L. 632      1190  LOAD_FAST                'root'
         1192_1194  POP_JUMP_IF_FALSE  1258  'to 1258'

 L. 633      1196  SETUP_EXCEPT       1212  'to 1212'

 L. 634      1198  LOAD_FAST                'self'
             1200  LOAD_METHOD              configure_root
             1202  LOAD_FAST                'root'
             1204  CALL_METHOD_1         1  '1 positional argument'
             1206  POP_TOP          
           1208_0  COME_FROM           374  '374'
             1208  POP_BLOCK        
             1210  JUMP_FORWARD       1258  'to 1258'
           1212_0  COME_FROM_EXCEPT   1196  '1196'

 L. 635      1212  DUP_TOP          
             1214  LOAD_GLOBAL              Exception
             1216  COMPARE_OP               exception-match
         1218_1220  POP_JUMP_IF_FALSE  1256  'to 1256'
             1222  POP_TOP          
             1224  STORE_FAST               'e'
             1226  POP_TOP          
             1228  SETUP_FINALLY      1244  'to 1244'

 L. 636      1230  LOAD_GLOBAL              ValueError
             1232  LOAD_STR                 'Unable to configure root logger'
             1234  CALL_FUNCTION_1       1  '1 positional argument'

 L. 637      1236  LOAD_FAST                'e'
             1238  RAISE_VARARGS_2       2  'exception instance with __cause__'
             1240  POP_BLOCK        
             1242  LOAD_CONST               None
           1244_0  COME_FROM_FINALLY  1228  '1228'
             1244  LOAD_CONST               None
             1246  STORE_FAST               'e'
             1248  DELETE_FAST              'e'
             1250  END_FINALLY      
           1252_0  COME_FROM           418  '418'
             1252  POP_EXCEPT       
             1254  JUMP_FORWARD       1258  'to 1258'
           1256_0  COME_FROM          1218  '1218'
             1256  END_FINALLY      
           1258_0  COME_FROM          1254  '1254'
           1258_1  COME_FROM          1210  '1210'
           1258_2  COME_FROM          1192  '1192'
           1258_3  COME_FROM           422  '422'
           1258_4  COME_FROM           354  '354'
             1258  POP_BLOCK        
             1260  LOAD_CONST               None
           1262_0  COME_FROM_FINALLY    74  '74'

 L. 639      1262  LOAD_GLOBAL              logging
             1264  LOAD_METHOD              _releaseLock
             1266  CALL_METHOD_0         0  '0 positional arguments'
             1268  POP_TOP          
             1270  END_FINALLY      

Parse error at or near `POP_BLOCK' instruction at offset 1208

    def configure_formatter(self, config):
        if '()' in config:
            factory = config['()']
            try:
                result = self.configure_custom(config)
            except TypeError as te:
                try:
                    if "'format'" not in str(te):
                        raise
                    config['fmt'] = config.pop('format')
                    config['()'] = factory
                    result = self.configure_custom(config)
                finally:
                    te = None
                    del te

        else:
            fmt = config.get('format', None)
            dfmt = config.get('datefmt', None)
            style = config.get('style', '%')
            cname = config.get('class', None)
            if not cname:
                c = logging.Formatter
            else:
                c = _resolve(cname)
            result = c(fmt, dfmt, style)
        return result

    def configure_filter(self, config):
        if '()' in config:
            result = self.configure_custom(config)
        else:
            name = config.get('name', '')
            result = logging.Filter(name)
        return result

    def add_filters(self, filterer, filters):
        for f in filters:
            try:
                filterer.addFilter(self.config['filters'][f])
            except Exception as e:
                try:
                    raise ValueError('Unable to add filter %r' % f) from e
                finally:
                    e = None
                    del e

    def configure_handler(self, config):
        config_copy = dict(config)
        formatter = config.pop('formatter', None)
        if formatter:
            try:
                formatter = self.config['formatters'][formatter]
            except Exception as e:
                try:
                    raise ValueError('Unable to set formatter %r' % formatter) from e
                finally:
                    e = None
                    del e

            level = config.pop('level', None)
            filters = config.pop('filters', None)
            if '()' in config:
                c = config.pop('()')
                if not callable(c):
                    c = self.resolve(c)
                factory = c
        else:
            cname = config.pop('class')
            klass = self.resolve(cname)
        if issubclass(klass, logging.handlers.MemoryHandler) and 'target' in config:
            try:
                th = self.config['handlers'][config['target']]
                if not isinstance(th, logging.Handler):
                    config.update(config_copy)
                    raise TypeError('target not configured yet')
                config['target'] = th
            except Exception as e:
                try:
                    raise ValueError('Unable to set target handler %r' % config['target']) from e
                finally:
                    e = None
                    del e

        else:
            if issubclass(klass, logging.handlers.SMTPHandler) and 'mailhost' in config:
                config['mailhost'] = self.as_tuple(config['mailhost'])
            else:
                if issubclass(klass, logging.handlers.SysLogHandler):
                    if 'address' in config:
                        config['address'] = self.as_tuple(config['address'])
                    factory = klass
                else:
                    props = config.pop('.', None)
                    kwargs = {k:config[k] for k in config if valid_ident(k)}
                    try:
                        result = factory(**kwargs)
                    except TypeError as te:
                        try:
                            if "'stream'" not in str(te):
                                raise
                            kwargs['strm'] = kwargs.pop('stream')
                            result = factory(**kwargs)
                        finally:
                            te = None
                            del te

                if formatter:
                    result.setFormatter(formatter)
                if level is not None:
                    result.setLevel(logging._checkLevel(level))
                if filters:
                    self.add_filters(result, filters)
                if props:
                    for name, value in props.items():
                        setattr(result, name, value)

                return result

    def add_handlers(self, logger, handlers):
        for h in handlers:
            try:
                logger.addHandler(self.config['handlers'][h])
            except Exception as e:
                try:
                    raise ValueError('Unable to add handler %r' % h) from e
                finally:
                    e = None
                    del e

    def common_logger_config(self, logger, config, incremental=False):
        level = config.get('level', None)
        if level is not None:
            logger.setLevel(logging._checkLevel(level))
        if not incremental:
            for h in logger.handlers[:]:
                logger.removeHandler(h)

            handlers = config.get('handlers', None)
            if handlers:
                self.add_handlers(logger, handlers)
            filters = config.get('filters', None)
            if filters:
                self.add_filters(logger, filters)

    def configure_logger(self, name, config, incremental=False):
        logger = logging.getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', None)
        if propagate is not None:
            logger.propagate = propagate

    def configure_root(self, config, incremental=False):
        root = logging.getLogger()
        self.common_logger_config(root, config, incremental)


dictConfigClass = DictConfigurator

def dictConfig(config):
    dictConfigClass(config).configure()


def listen(port=DEFAULT_LOGGING_CONFIG_PORT, verify=None):

    class ConfigStreamHandler(StreamRequestHandler):

        def handle(self):
            try:
                conn = self.connection
                chunk = conn.recv(4)
                if len(chunk) == 4:
                    slen = struct.unpack('>L', chunk)[0]
                    chunk = self.connection.recv(slen)
                    while len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))

                    if self.server.verify is not None:
                        chunk = self.server.verify(chunk)
                    if chunk is not None:
                        chunk = chunk.decode('utf-8')
                        try:
                            import json
                            d = json.loads(chunk)
                            dictConfig(d)
                        except Exception:
                            file = io.StringIO(chunk)
                            try:
                                fileConfig(file)
                            except Exception:
                                traceback.print_exc()

                    if self.server.ready:
                        self.server.ready.set()
            except OSError as e:
                try:
                    if e.errno != RESET_ERROR:
                        raise
                finally:
                    e = None
                    del e

    class ConfigSocketReceiver(ThreadingTCPServer):
        allow_reuse_address = 1

        def __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT, handler=None, ready=None, verify=None):
            ThreadingTCPServer.__init__(self, (host, port), handler)
            logging._acquireLock()
            self.abort = 0
            logging._releaseLock()
            self.timeout = 1
            self.ready = ready
            self.verify = verify

        def serve_until_stopped(self):
            import select
            abort = 0
            while not abort:
                rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
                if rd:
                    self.handle_request()
                logging._acquireLock()
                abort = self.abort
                logging._releaseLock()

            self.server_close()

    class Server(threading.Thread):

        def __init__(self, rcvr, hdlr, port, verify):
            super(Server, self).__init__()
            self.rcvr = rcvr
            self.hdlr = hdlr
            self.port = port
            self.verify = verify
            self.ready = threading.Event()

        def run(self):
            global _listener
            server = self.rcvr(port=(self.port), handler=(self.hdlr), ready=(self.ready),
              verify=(self.verify))
            if self.port == 0:
                self.port = server.server_address[1]
            self.ready.set()
            logging._acquireLock()
            _listener = server
            logging._releaseLock()
            server.serve_until_stopped()

    return Server(ConfigSocketReceiver, ConfigStreamHandler, port, verify)


def stopListening():
    global _listener
    logging._acquireLock()
    try:
        if _listener:
            _listener.abort = 1
            _listener = None
    finally:
        logging._releaseLock()