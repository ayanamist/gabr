from __future__ import absolute_import

import logging
import urllib
import urlparse

import requests
import requests_oauthlib


BASE_URL = "https://api.twitter.com"  # w/o trail slash.
OAUTH_REQUEST_TOKEN_URL = "%s/oauth/request_token" % BASE_URL
OAUTH_ACCESS_TOKEN_URL = "%s/oauth/access_token" % BASE_URL
OAUTH_AUTHORIZE_URL = "%s/oauth/authorize" % BASE_URL

API_VERSION = "1.1"
USER_AGENT = "gabr/1.0"
SIGNATURE_TYPE = "auth_header"


class Error(IOError):
    def __init__(self, message, response=None):
        super(Error, self).__init__(message)
        self.response = response


class API(object):
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        self.client = requests.Session()
        self.client.headers = {"User-Agent": USER_AGENT}

    def bind_auth(self, oauth_token=None, oauth_token_secret=None):
        self.client.auth = requests_oauthlib.OAuth1(self.consumer_key, self.consumer_secret, oauth_token,
                                                    oauth_token_secret, signature_type=SIGNATURE_TYPE)

    def request(self, method, endpoint, params=None, files=None, **kwargs):
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            url = endpoint
        else:
            url = "%s/%s/%s.json" % (BASE_URL, API_VERSION, endpoint.lower())

        if kwargs:
            if params is None:
                params = kwargs
            else:
                params.update(kwargs)

        if method.upper() == "GET" and params:
            parts = urlparse.urlsplit(url)
            if parts.query:
                parts.query = "%s&%s" % (parts.query, urllib.urlencode(params))
            url = urlparse.urlunsplit(parts)

        response = self.client.request(method=method, url=url, params=params, files=files)
        json_content = None
        if url.endswith(".json"):
            try:
                json_content = response.json()
            except ValueError:  # not a json, sometimes maybe a XML file.
                logging.debug("%d: Not a JSON response for %s %s:\n%s" % (response.status_code,
                                                                          method, url, response.content))
                raise Error("Not a JSON response.", response=response)
        if response.status_code > 304:
            message = "%d %s" % (response.status_code, response.reason)
            if json_content:
                errors = json_content.get("errors")
                if errors:
                    for error in errors:
                        message += ", \"%s (%d)\"" % (error["message"], error["code"])
                else:
                    error = json_content.get("error")
                    if error:
                        message += ", \"%s\"" % error
                    else:
                        # Twitter maybe have other error format, we should save it for further digging.
                        logging.error("JSON Errors: %s" % response.content)
            raise Error(message, response=response)
        return response

    def get_authentication_tokens(self, callback_url=None):
        if callback_url:
            request_args = {"oauth_callback": callback_url}
        else:
            request_args = None

        response = self.request("GET", OAUTH_REQUEST_TOKEN_URL, params=request_args)
        return dict(urlparse.parse_qsl(response.content))

    def get_authorized_tokens(self):
        response = self.request("GET", OAUTH_ACCESS_TOKEN_URL)
        return dict(urlparse.parse_qsl(response.content))