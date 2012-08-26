import flask

from . import timeline
from application import app

@app.route("/rss")
def home_rss():
    results = timeline.timeline("Home", flask.g.api.get_home_timeline)
    resp = flask.make_response(flask.render_template("rss.xml", **results))
    resp.headers["Content-Type"] = "application/rss+xml"
    return resp

