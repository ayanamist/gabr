from __future__ import absolute_import

import base64
import email.utils
import functools
import json
import time
import zlib

from google.appengine.api import memcache

import flask

from application import app
from application import utils
from application.libs import crypto
from application.libs import indicesreplace
from application.utils import decorators
from application.views import timeline


@app.route("/rss")
@decorators.login_required
@decorators.templated("rss.html")
def rss_url():
    return {
        "title": "RSS",
        "rss_url": utils.abs_url_for("home_rss", sid=base64.urlsafe_b64encode(
            crypto.encrypt("%s:%s" % (flask.session["oauth_token"], flask.session["oauth_token_secret"]),
                           app.config["SECRET_KEY"]),
        )),
    }


@app.route("/rss/<sid>")
def home_rss(sid):
    sid = str(sid)
    try:
        sid = crypto.decrypt(base64.urlsafe_b64decode(sid), app.config["SECRET_KEY"])
        oauth_token, oauth_token_secret = sid.split(":", 1)
    except (ValueError, TypeError):
        return "Invalid sid."
    flask.g.api.bind_auth(oauth_token, oauth_token_secret)
    params = utils.parse_params()
    if params.get("count"):
        params["count"] = 100
    cached = memcache.get(sid + str(params))
    if cached:
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
        for tweet in data["results"]:
            urls = tweet.get("entities", {}).get("urls", [])
            new_text = indicesreplace.IndicesReplace(tweet["text"])
            for url in urls:
                start, stop = url["indices"]
                new_text.replace_indices(start, stop, url["display_url"])
            tweet["rss_title"] = unicode(new_text).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        memcache.set(sid + str(params), zlib.compress(json.dumps(data["results"]), 9), time=120)
    data["now"] = email.utils.formatdate()
    resp = flask.make_response(flask.render_template("rss.xml", **data))
    resp.headers["Content-Type"] = "application/rss+xml; charset=utf-8"
    return resp

