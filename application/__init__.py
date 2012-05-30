import datetime

import flask

app = flask.Flask("application")
app.config.from_object("config")
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)
app.config["SESSION_COOKIE_SECURE"] = True

import views
