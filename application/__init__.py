from __future__ import absolute_import

import os
import sys

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
lib_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "lib"))
for zip_file in os.listdir(lib_path):
    sys.path.insert(0, os.path.join(lib_path, zip_file))

import flask

app = flask.Flask("application")

# Config from os.environ are all strings, but here only accepts integer.
app.config["PERMANENT_SESSION_LIFETIME"] = 31536000  # one year
# import all configs from app.yaml
os_names = (
    "SITE_NAME",
    "SESSION_COOKIE_PATH",
    "CONSUMER_KEY",
    "CONSUMER_SECRET",
    "SECRET_KEY",
)
for name in os_names:
    app.config[name] = os.environ[name]
app.config["TWIP_T_MODE"] = os.environ.get("TWIP_T_MODE", None)

from application.utils import monkey_patch

monkey_patch.patch_all(app)

from application import views
from application import routes