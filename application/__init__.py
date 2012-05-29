import flask

app = flask.Flask("application")
app.config.from_object("config")

import views
