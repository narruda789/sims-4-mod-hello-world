# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\text.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1479 bytes
__all__ = [
 'MIMEText']
from email.charset import Charset
from email.mime.nonmultipart import MIMENonMultipart

class MIMEText(MIMENonMultipart):

    def __init__(self, _text, _subtype='plain', _charset=None, *, policy=None):
        if _charset is None:
            try:
                _text.encode('us-ascii')
                _charset = 'us-ascii'
            except UnicodeEncodeError:
                _charset = 'utf-8'

        (MIMENonMultipart.__init__)(self, 'text', _subtype, policy=policy, **{'charset': str(_charset)})
        self.set_payload(_text, _charset)