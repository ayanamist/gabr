from __future__ import absolute_import

import copy
import os
import re
import time
import urllib
import urlparse
from email import utils

import flask


is_support_versions = not not os.environ.get("VERSIONS", None)


def abs_url_for(endpoint, **values):
    host = flask.request.host
    if not is_support_versions:
        host = re.sub(r'^[0-9]+\-dot\-', '', flask.request.host)
    return urlparse.urljoin("https://" + host, flask.url_for(endpoint, **values))


def remove_status_by_id(iterable, max_id):
    if max_id:
        for i, result in enumerate(iterable):
            if result.get("id_str") == max_id or result.get("max_position") == max_id:
                del iterable[i]
    return iterable


def do_item(obj, name):
    try:
        value = obj[name]
    except (TypeError, KeyError):
        pass
    else:
        return value


def do_rfc822(obj):
    return utils.formatdate(time.mktime(utils.parsedate(obj)))


def build_next_page_url(data, params, key_name="id_str"):
    new_params = copy.copy(params)
    try:
        new_params["max_id"] = data[-1][key_name]
        return "?" + urllib.urlencode(new_params)
    except IndexError:
        pass
