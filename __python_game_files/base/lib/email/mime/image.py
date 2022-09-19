# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\image.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1876 bytes
__all__ = [
 'MIMEImage']
import imghdr
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart

class MIMEImage(MIMENonMultipart):

    def __init__(self, _imagedata, _subtype=None, _encoder=encoders.encode_base64, *, policy=None, **_params):
        if _subtype is None:
            _subtype = imghdr.what(None, _imagedata)
        if _subtype is None:
            raise TypeError('Could not guess image MIME subtype')
        (MIMENonMultipart.__init__)(self, 'image', _subtype, policy=policy, **_params)
        self.set_payload(_imagedata)
        _encoder(self)