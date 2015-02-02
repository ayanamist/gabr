from __future__ import absolute_import

import functools
import logging
import urllib
import urlparse

import requests
import requests_oauthlib


BASE_URL = "https://api.twitter.com"  # w/o trail slash.
OAUTH_REQUEST_TOKEN_URL = "%s/oauth/request_token" % BASE_URL
OAUTH_ACCESS_TOKEN_URL = "%s/oauth/access_token" % BASE_URL
OAUTH_AUTHORIZE_URL = "%s/oauth/authorize" % BASE_URL

USER_AGENT = "gabr/1.0"
SIGNATURE_TYPE = "auth_header"


class Error(IOError):
    def __init__(self, message, response=None):
        super(Error, self).__init__(message)
        self.response = response


class API(object):
    def __init__(self, consumer_key, consumer_secret, twip_t_mode_base_url=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.twip_t_mode_base_url = twip_t_mode_base_url

        self.client = requests.Session()
        self.client.headers = {"User-Agent": USER_AGENT}

        self.get = functools.partial(self.request, "GET")
        self.post = functools.partial(self.request, "POST")

    def bind_auth(self, oauth_token=None, oauth_token_secret=None, oauth_verifier=None):
        self.client.auth = requests_oauthlib.OAuth1(self.consumer_key, self.consumer_secret,
                                                    oauth_token, oauth_token_secret, verifier=oauth_verifier,
                                                    signature_type=SIGNATURE_TYPE)

    def request(self, method, endpoint, params=None, files=None, version="1.1", use_t_mode=False, **kwargs):
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            url = endpoint
        else:
            url = "%s/%s/%s.json" % (BASE_URL, version, endpoint.lower())

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

        prepped = self.client.prepare_request(requests.Request(method=method, url=url, params=params, files=files))
        if use_t_mode and self.twip_t_mode_base_url:
            prepped.url = self.twip_t_mode_base_url + prepped.url[len(BASE_URL):]
        try:
            response = self.client.send(prepped)
        except requests.RequestException as e:
            raise Error(str(e))
        json_content = None
        if url.endswith(".json"):
            try:
                json_content = response.json()
            except ValueError:  # not a json, sometimes maybe a XML file.
                logging.debug("%d: Not a JSON response for %s %s:\n%s" % (response.status_code,
                                                                          method, url, response.content))
                raise Error("Not a JSON response.", response=response)
        message = ""
        if response.status_code > 304:
            message = "%d %s" % (response.status_code, response.reason)
        if json_content and isinstance(json_content, dict):
            errors = json_content.get("errors")
            if not errors:
                results = json_content.get("results")
                if results:
                    errors = results.get("errors")
            if errors:
                # Twitter will return anything in errors.
                if isinstance(errors, basestring):
                    err_msg = errors
                elif hasattr(errors, "__iter__"):
                    err_msg = ", ".join("\"%s (%d)\"" % (error["message"], error["code"]) for error in errors)
                else:
                    err_msg = str(errors)
            else:
                error = json_content.get("error")
                if error:
                    err_msg = error
                elif response.status_code > 304:
                    err_msg = "unknown error for unexpected response"
                    # Twitter maybe have other error format, we should save it for further digging.
                    logging.error("JSON Errors: %s" % response.content)
                else:
                    err_msg = None
            if err_msg:
                message = ", ".join(filter(lambda x: not not x, (message, err_msg)))
        if message:
            raise Error(message, response=response)
        return response

    def get_authentication_tokens(self, callback_url=None):
        if callback_url:
            request_args = {"oauth_callback": callback_url}
        else:
            request_args = None

        response = self.request("POST", OAUTH_REQUEST_TOKEN_URL, params=request_args)
        request_tokens = dict(urlparse.parse_qsl(response.content))
        request_tokens["auth_url"] = "%s?%s" % (OAUTH_AUTHORIZE_URL,
                                                urllib.urlencode({"oauth_token": request_tokens["oauth_token"]}))
        return request_tokens

    def get_authorized_tokens(self, **kwargs):
        response = self.request("POST", OAUTH_ACCESS_TOKEN_URL, kwargs)
        return dict(urlparse.parse_qsl(response.content))