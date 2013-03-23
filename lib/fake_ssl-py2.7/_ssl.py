"""
This file is used to solve requests module compatibility.
Usually requests under Google App Engine will throw error like below:
NameError: name 'CERT_NONE' is not defined
So we must ensure that import ssl will not throw any exceptions any more.
Using this file will ensure all things are defined although not implemented in fact.
"""
# encoding: utf-8
# module _ssl
# from C:\Python27\DLLs\_ssl.pyd
# by generator 1.121

# imports
import socket as __socket


# Variables with simple values

CERT_NONE = 0
CERT_OPTIONAL = 1
CERT_REQUIRED = 2

OPENSSL_VERSION = 'OpenSSL 0.9.8l 5 Nov 2009'

OPENSSL_VERSION_NUMBER = 9470159L

PROTOCOL_SSLv2 = 0
PROTOCOL_SSLv23 = 2
PROTOCOL_SSLv3 = 1
PROTOCOL_TLSv1 = 3

SSL_ERROR_EOF = 8

SSL_ERROR_INVALID_ERROR_CODE = 9

SSL_ERROR_SSL = 1
SSL_ERROR_SYSCALL = 5

SSL_ERROR_WANT_CONNECT = 7
SSL_ERROR_WANT_READ = 2
SSL_ERROR_WANT_WRITE = 3

SSL_ERROR_WANT_X509_LOOKUP = 4

SSL_ERROR_ZERO_RETURN = 6

# functions

def RAND_add(string, entropy): # real signature unknown; restored from __doc__
    """
    RAND_add(string, entropy)

    Mix string into the OpenSSL PRNG state.  entropy (a float) is a lower
    bound on the entropy contained in string.  See RFC 1750.
    """
    pass


def RAND_egd(path): # real signature unknown; restored from __doc__
    """
    RAND_egd(path) -> bytes

    Queries the entropy gather daemon (EGD) on the socket named by 'path'.
    Returns number of bytes read.  Raises SSLError if connection to EGD
    fails or if it does provide enough data to seed PRNG.
    """
    return ""


def RAND_status(): # real signature unknown; restored from __doc__
    """
    RAND_status() -> 0 or 1

    Returns 1 if the OpenSSL PRNG has been seeded with enough data and 0 if not.
    It is necessary to seed the PRNG with RAND_add() on some platforms before
    using the ssl() function.
    """
    pass


def sslwrap(socket, server_side, keyfile=None, certfile=None, certs_mode=None, protocol=None, cacertsfile=None,
            ciphers=None): # real signature unknown; restored from __doc__
    """
    sslwrap(socket, server_side, [keyfile, certfile, certs_mode, protocol,
                                  cacertsfile, ciphers]) -> sslobject
    """
    pass


def _test_decode_cert(*args, **kwargs): # real signature unknown
    pass


# classes

class SSLError(__socket.error):
    pass


class SSLType(object):
    # no doc
    def __init__(self, *args, **kwargs): # real signature unknown
        pass


# variables with complex values

OPENSSL_VERSION_INFO = (
    0,
    9,
    8,
    12,
    15,
)

SSLContext = None
HAS_SNI = False