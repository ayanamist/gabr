import datetime
import os
import sys

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
egg_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "egg"))
for egg in os.listdir(egg_path):
    sys.path.append(os.path.join(egg_path, egg))

import flask
import jinja2

from .lib import twitter
from .lib import render

app = flask.Flask("application")
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)
app.config["SESSION_COOKIE_PATH"] = "/"

# import all configs from app.yaml
for name in (x for x in os.environ.keys() if x.isupper()):
    app.config[name] = os.environ[name]

__import__("views", globals(), locals(), [], -1)

@app.before_request
def before_request():
    g = flask.g
    g.screen_name = flask.session.get("screen_name")
    g.api = twitter.Api(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
    if g.screen_name:
        g.api.set_access_token(flask.session["oauth_token"], flask.session["oauth_token_secret"])


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

app.jinja_env.globals.update(
    prerender_tweet=render.prerender_tweet,
    isinstance=isinstance,
    Status=twitter.Status,
    Activity=twitter.Activity,
)



