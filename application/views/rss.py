import base64
import email.utils
import os

import flask
from werkzeug.contrib import securecookie
from werkzeug import wsgi

from application import app
from ..lib import twitter
from . import timeline

root_url = wsgi.get_current_url(os.environ, root_only=True, strip_querystring=True, host_only=True)
abs_url_for = lambda endpoint, **values: root_url + flask.url_for(endpoint, **values)


@app.route("/rss")
def home_rss():
    g = flask.g
    session = securecookie.SecureCookie.unserialize(base64.b64decode(flask.request.args.get("sid")),
        app.config["SECRET_KEY"])
    g.screen_name = session.get("screen_name")
    g.api = twitter.Api(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
    if g.screen_name:
        g.api.set_access_token(session["oauth_token"], session["oauth_token_secret"])
    results = timeline.timeline("Home", g.api.get_home_timeline)
    results["pub_date"] = email.utils.formatdate()
    results["abs_url_for"] = abs_url_for
    resp = flask.make_response(flask.render_template("rss.xml", **results))
    resp.headers["Content-Type"] = "application/rss+xml"
    return resp

