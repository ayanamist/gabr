import datetime
import os

import flask

app = flask.Flask("application")
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["CONSUMER_KEY"] = os.environ["CONSUMER_KEY"]
app.config["CONSUMER_SECRET"] = os.environ["CONSUMER_SECRET"]
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["INVITE_CODE"] = os.environ["INVITE_CODE"]

import views
