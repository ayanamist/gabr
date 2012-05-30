import datetime
import os
import sys

egg_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "egg"))
for egg in os.listdir(egg_path):
    sys.path.append(os.path.join(egg_path, egg))

import flask

app = flask.Flask("application")
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["CONSUMER_KEY"] = os.environ["CONSUMER_KEY"]
app.config["CONSUMER_SECRET"] = os.environ["CONSUMER_SECRET"]
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["INVITE_CODE"] = os.environ["INVITE_CODE"]

import views
