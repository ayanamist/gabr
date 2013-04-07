from __future__ import absolute_import

from Crypto.Cipher import AES

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[0:-ord(s[-1])]

def encrypt(raw, secret):
    raw = pad(raw)
    cipher = AES.new(pad(secret), AES.MODE_ECB)
    return cipher.encrypt(raw)


def decrypt(enc, secret):
    cipher = AES.new(pad(secret), AES.MODE_ECB)
    return unpad(cipher.decrypt(enc))
