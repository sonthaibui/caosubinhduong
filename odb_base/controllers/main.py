# -*- coding: utf-8 -*-
import base64, re, sys, io, unicodedata
from odoo.tools import ustr

import logging
_logger = logging.getLogger(__name__)

try:
    import qrcode
except ImportError:
    _logger.warning("The qrcode python library is not installed, amount-to-text features won't be fully available.")
    
try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None
    
def qr_imgage(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    temp = io.BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    return qr_img

def up_round_1000(value):
    number = value - round(value, -3)
    if number >= 500:
        value = round(value, -3) + 1
    else:
        value = round(value, -3)
    return value 

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}

#vietnam
def vietnam_utf8(s):
    s = s and ustr(s).strip() or False
    if not s:
        return s
    s = s.lower()
    for regex, replace in patterns.items():
        s = re.sub(regex, replace, s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    return s

def _vietnam_phonenumber(phonenumber):
    if not phonenumber:
        return phonenumber
    for head in ['0084', '084', '84']:
        if phonenumber.startswith(head):
            phonenumber = phonenumber.replace(head, '0', 1)
            break
    return phonenumber

## for value string
def _remove_symbol(s):
    if not s:
        return s
    
    s = ustr(s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub('[^a-zA-Z0-9\n\.]','',s)
    s = re.sub(r"\s+", "", s, flags=re.UNICODE)
    return s
    
def _remove_space(s):
    if not s:
        return s
    
    s = ustr(s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r"\s+", "", s, flags=re.UNICODE)
    
    return s
    