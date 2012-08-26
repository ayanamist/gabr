import base64
import logging
import os
import sys

# Mute noisy requests logging.
# In fact following statements have no effect on Google App Engine. requests still log.
class MyLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None):
        if not self.name.startswith("requests"):
            return super(MyLogger, self)._log(level, msg, args, exc_info, extra)

logging.setLoggerClass(MyLogger)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger('requests').addHandler(logging.NullHandler())

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
lib_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "lib"))
for zip_file in os.listdir(lib_path):
    sys.path.insert(0, os.path.join(lib_path, zip_file))

import flask
import jinja2
import twython
from werkzeug.contrib import securecookie

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

