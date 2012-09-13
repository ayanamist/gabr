import email.utils
import functools

import flask

from .import timeline
from ..import utils
from application import app

@app.route("/rss")
def home_rss():
    params = utils.parse_params()
    data = timeline.timeline("Home", functools.partial(flask.g.api.getHomeTimeline, **params))
    data["results"].reverse() # Google Reader will not sort it themselves.
    data["now"] = email.utils.formatdate()
    resp = flask.make_response(flask.render_template("rss.xml", **data))
    resp.headers["Content-Type"] = "application/rss+xml"
    return resp

