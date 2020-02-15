from __future__ import absolute_import

import base64
import email.utils
import functools
import json
import logging
import time
import zlib

from google.appengine.api import memcache
from google.appengine.api.app_identity import app_identity

import flask

from application import utils
from application.libs import crypto
from application.libs import indicesreplace
from application.utils import decorators
from application.views import timeline


@decorators.login_required
@decorators.templated("rss.html")
def rss_url():
    return {
        "title": "RSS",
        "rss_url": utils.abs_url_for("home_rss", sid=base64.urlsafe_b64encode(
            crypto.encrypt("%s:%s" % (flask.session["oauth_token"], flask.session["oauth_token_secret"]),
                           flask.current_app.config["SECRET_KEY"]),
        )),
    }


def home_rss(sid):
    flask.g.host = app_identity.get_default_version_hostname()
    sid = str(sid)
    try:
        sid = crypto.decrypt(base64.urlsafe_b64decode(sid), flask.current_app.config["SECRET_KEY"])
        oauth_token, oauth_token_secret = sid.split(":", 1)
    except (ValueError, TypeError):
        return "Invalid sid."
    flask.g.api.bind_auth(oauth_token, oauth_token_secret)
    params = flask.request.args.to_dict()
    params["tweet_mode"] = "extended"
    if "count" not in params:
        params["count"] = 200
    cached = memcache.get(sid + str(params))
    if cached:
        logging.debug("fetched from memcache")
        data = {
            "title": "Home",
            "results": json.loads(zlib.decompress(cached))
        }
    else:
        data = timeline.timeline("Home",
                                 functools.partial(flask.g.api.get,
                                                   "statuses/home_timeline",
                                                   **params))
        data["results"].sort(
            cmp=lambda a, b: int(time.mktime(email.utils.parsedate(a["created_at"])) - time.mktime(
                email.utils.parsedate(b["created_at"]))),
            reverse=True)
        logging.debug("rss result: %d", len(data["results"]))
        for tweet in data["results"]:
            new_text = indicesreplace.IndicesReplace(tweet["full_text"])
            entities = tweet.get("entities", {})
            for url in entities.get("urls", []):
                start, stop = url["indices"]
                new_text.replace_indices(start, stop, url["display_url"])
            for url in entities.get("media", []):
                start, stop = url["indices"]
                new_text.replace_indices(start, stop, url["display_url"])
            tweet["rss_title"] = unicode(new_text).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
            id_str = tweet["id_str"]
            retweeted_status = tweet.get("retweeted_status")
            if retweeted_status:
                id_str = retweeted_status["id_str"]
            tweet["rss_link"] = "https://twitter.com/i/status/%s" % id_str
        memcache.set(sid + str(params), zlib.compress(json.dumps(data["results"]), 9), time=120)
    data["now"] = email.utils.formatdate()
    resp = flask.make_response(flask.render_template("rss.xml", **data))
    resp.headers["Content-Type"] = "application/rss+xml; charset=utf-8"
    return resp

