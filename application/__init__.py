import os
import types

import flask

app = flask.Flask("application")
app.config.from_object("config")

# because config.py may be modified by newbie, so move DEBUG setting to here.
app.config["DEBUG"] = False
if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    app.config["DEBUG"] = True

from views import login