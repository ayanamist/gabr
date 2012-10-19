import os

import flask
import twython

from application import app

# import all views
for view in (x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x != "__init__.py"):
    __import__("%s" % view, globals(), locals(), [], -1)

@app.before_request
def before_request():
    flask.session.permanent = True

    flask.g.screen_name = flask.session.get("screen_name")
    oauth_token = flask.session.get("oauth_token")
    oauth_token_secret = flask.session.get("oauth_token_secret")
    flask.g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"],
        oauth_token, oauth_token_secret)



