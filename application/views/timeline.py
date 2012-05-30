import flask

from application import app
from ..lib import decorators

@app.route("/")
@decorators.login_required
def home_timeline():
    return "OK"