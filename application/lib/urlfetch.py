import json
import zlib

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import *

from . import decorators
from . import oauth

accept_encoding = "Accept-Encoding"
content_encoding = "Content-Encoding"

class Future(object):
    def __init__(self, rpc):
        self.rpc = rpc

    def get_result(self):
        result = self.rpc.get_result()
        if result.headers.get(content_encoding, "").lower() == "gzip":
            try:
                result.content = zlib.decompress(result.content, 16 + zlib.MAX_WBITS)
            except zlib.error:
                pass
            else:
                result.headers.pop(content_encoding, None)
        return result


def fetch_async(url, payload=None, headers=None):
    if headers is None:
        headers = dict()
    if accept_encoding.lower() not in [x.lower() for x in headers.keys()]:
        headers[accept_encoding] = "gzip"
    if payload is not None:
        method = "POST"
    else:
        method = "GET"
    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(rpc, url, payload=payload, method=method, headers=headers, allow_truncated=False,
        follow_redirects=False)
    return Future(rpc)


def sync_wrapper(func):
    def invoke_func(*args, **kwargs):
        return func(*args, **kwargs).get_result()

    return invoke_func

fetch = sync_wrapper(fetch_async)
