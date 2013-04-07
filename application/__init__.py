from __future__ import absolute_import

import os
import sys

# add all egg files to sys.path
# use egg files instead of plain directory for beautiful directory structure and faster upload
lib_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "lib"))
for zip_file in os.listdir(lib_path):
    sys.path.insert(0, os.path.join(lib_path, zip_file))

import flask

from application.utils import monkey_patch

app = flask.Flask("application")
monkey_patch.patch_all(app)

# Config from os.environ are all strings, but here only accepts integer.
app.config["PERMANENT_SESSION_LIFETIME"] = 31536000  # one year
# import all configs from app.yaml
for name in (x for x in os.environ.keys() if x.isupper()):
    app.config[name] = os.environ[name]

__import__("views", globals(), locals(), [], -1)
