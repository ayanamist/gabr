import base64
import email.utils
import functools
import operator

import flask
import twython
from application.utils import crypto

from .import timeline
from ..import utils
from application import app

@app.route("/rss/<sid>")
def home_rss(sid):
    try:
        sid = crypto.decrypt(base64.urlsafe_b64decode(str(sid)), app.config["SECRET_KEY"])
        oauth_token, oauth_token_secret = sid.split(":", 1)
    except (ValueError, TypeError):
        return "Invalid sid."
    flask.g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"],
        oauth_token, oauth_token_secret)

    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline.timeline("Home", functools.partial(flask.g.api.getHomeTimeline, **params))
    data["results"].sort(key=operator.itemgetter("id"), reverse=True)
    data["now"] = email.utils.formatdate()
    resp = flask.make_response(flask.render_template("rss.xml", **data))
    resp.headers["Content-Type"] = "application/rss+xml"
    return resp

