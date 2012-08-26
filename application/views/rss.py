import functools

import flask

from . import timeline
from ..import utils
from application import app

@app.route("/rss")
def home_rss():
    params = utils.parse_params()
    params["include_entities"] = 1
    results = timeline.timeline("Home", functools.partial(flask.g.api.getHomeTimeline, **params))
    resp = flask.make_response(flask.render_template("rss.xml", **results))
    resp.headers["Content-Type"] = "application/rss+xml"
    return resp

