import base64
import logging
import os
import sys

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
lib_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "lib"))
for zip_file in os.listdir(lib_path):
    sys.path.insert(0, os.path.join(lib_path, zip_file))

import flask
import jinja2
import twython
from werkzeug.contrib import securecookie

# Mute noisy requests logging.
logging.getLogger("requests").setLevel(logging.CRITICAL)
from requests.packages.oauthlib.oauth1 import rfc5849

rfc5849.logging.debug = lambda msg: None

# Patch requests not to verify SSL, it's unnecessary for GAE.
def requests_wrap(f):
    def wrapped(**kwargs):
        kwargs["verify"] = False
        return f(**kwargs)

    return wrapped

twython.twython.requests.session = requests_wrap(twython.twython.requests.session)

@jinja2.environmentfilter
def do_item(environment, obj, name):
    try:
        name = str(name)
    except UnicodeError:
        pass
    else:
        try:
            value = obj[name]
        except (TypeError, KeyError):
            pass
        else:
            return value
    return environment.undefined(obj=obj, name=name)

jinja2.filters.FILTERS["item"] = do_item

app = flask.Flask("application")
# Config from os.environ are all strings, but here only accepts integer.
app.config["PERMANENT_SESSION_LIFETIME"] = 31536000 # one year
# import all configs from app.yaml
for name in (x for x in os.environ.keys() if x.isupper()):
    app.config[name] = os.environ[name]

__import__("views", globals(), locals(), [], -1)

@app.before_request
def before_request():
    g = flask.g
    g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])

    sid = flask.request.args.get("sid")
    g.screen_name = None
    if sid:
        try:
            sid = securecookie.SecureCookie.unserialize(base64.b64decode(sid), app.config["SECRET_KEY"])
            g.screen_name = sid.get("screen_name")
        except Exception:
            sid = None

    oauth_token = None
    oauth_token_secret = None
    if g.screen_name:
        oauth_token = sid["oauth_token"]
        oauth_token_secret = sid["oauth_token_secret"]
    else:
        g.screen_name = flask.session.get("screen_name")
        if g.screen_name:
            oauth_token = flask.session["oauth_token"]
            oauth_token_secret = flask.session["oauth_token_secret"]
    if oauth_token and oauth_token_secret:
        g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"],
            oauth_token, oauth_token_secret)

