import flask

from application import app
from ..lib import decorators

@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    return {
        "title": "Home",
        }