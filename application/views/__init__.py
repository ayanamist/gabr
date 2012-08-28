import base64
import os

import flask
import twython
from werkzeug.contrib import securecookie

from application import app

# import all views
for view in (x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x != "__init__.py"):
    __import__("%s" % view, globals(), locals(), [], -1)

@app.before_request
def before_request():
    flask.session.permanent = True

    g = flask.g
    g.screen_name = None
    g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])

    oauth_token = None
    oauth_token_secret = None

    sid = flask.request.args.get("sid")
    if sid:
        try:
            sid = securecookie.SecureCookie.unserialize(base64.b64decode(sid), app.config["SECRET_KEY"])
            g.screen_name = sid.get("screen_name")
            oauth_token = sid["oauth_token"]
            oauth_token_secret = sid["oauth_token_secret"]
        except Exception:
            pass

    if g.screen_name and oauth_token and oauth_token_secret:
        pass
    else:
        g.screen_name = flask.session.get("screen_name")
        oauth_token = flask.session.get("oauth_token")
        oauth_token_secret = flask.session.get("oauth_token_secret")

    if oauth_token and oauth_token_secret:
        g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"],
            oauth_token, oauth_token_secret)


