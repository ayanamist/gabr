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
app.config["SESSION_COOKIE_PATH"] = "/"

# import all configs from app.yaml
for name in (x for x in os.environ.keys() if x.isupper()):
    app.config[name] = os.environ[name]

__import__("views", globals(), locals(), [], -1)