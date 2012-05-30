import datetime
import os
import sys

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
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

# import all views
for view in (x[:-3] for x in
    os.listdir(os.path.join(os.path.dirname(__file__), "views")) if x != "__init__.py"):
    __import__("views.%s" % view, globals(), locals(), [], -1)

