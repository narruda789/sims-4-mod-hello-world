# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_dummy_thread.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5280 bytes
__all__ = [
 'error', 'start_new_thread', 'exit', 'get_ident', 'allocate_lock',
 'interrupt_main', 'LockType']
TIMEOUT_MAX = 2147483648
error = RuntimeError

def start_new_thread(function, args, kwargs={}):
    global _interrupt
    global _main
    if type(args) != type(tuple()):
        raise TypeError('2nd arg must be a tuple')
    else:
        if type(kwargs) != type(dict()):
            raise TypeError('3rd arg must be a dict')
        _main = False
        try:
            function(*args, **kwargs)
        except SystemExit:
            pass
        except:
            import traceback
            traceback.print_exc()

    _main = True
    if _interrupt:
        _interrupt = False
        raise KeyboardInterrupt


def exit():
    raise SystemExit


def get_ident():
    return 1


def allocate_lock():
    return LockType()


def stack_size(size=None):
    if size is not None:
        raise error('setting thread stack size not supported')
    return 0


def _set_sentinel():
    return LockType()


class LockType(object):

    def __init__(self):
        self.locked_status = False

    def acquire(self, waitflag=None, timeout=-1):
        if waitflag is None or waitflag:
            self.locked_status = True
            return True
        else:
            self.locked_status = self.locked_status or True
            return True
        if timeout > 0:
            import time
            time.sleep(timeout)
        return False

    __enter__ = acquire

    def __exit__(self, typ, val, tb):
        self.release()

    def release(self):
        if not self.locked_status:
            raise error
        self.locked_status = False
        return True

    def locked(self):
        return self.locked_status

    def __repr__(self):
        return '<%s %s.%s object at %s>' % (
         'locked' if self.locked_status else 'unlocked',
         self.__class__.__module__,
         self.__class__.__qualname__,
         hex(id(self)))


_interrupt = False
_main = True

def interrupt_main():
    global _interrupt
    if _main:
        raise KeyboardInterrupt
    else:
        _interrupt = True