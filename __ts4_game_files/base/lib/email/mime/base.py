# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\base.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 946 bytes
__all__ = [
 'MIMEBase']
import email.policy
from email import message

class MIMEBase(message.Message):

    def __init__(self, _maintype, _subtype, *, policy=None, **_params):
        if policy is None:
            policy = email.policy.compat32
        message.Message.__init__(self, policy=policy)
        ctype = '%s/%s' % (_maintype, _subtype)
        (self.add_header)('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'