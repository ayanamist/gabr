import functools

import flask
import twython

from .. import utils
from ..utils import decorators
from application import app

def timeline(title, api_func):
    data = {
        "title": title,
        "results": tuple(),
        }
    try:
        results = api_func()
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        data["results"] = utils.remove_max_id(results, flask.request.args.get("max_id"))
    return data


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    return timeline("Home", functools.partial(flask.g.api.getHomeTimeline, **params))


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline.html")
def connect_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    return timeline("Connect", functools.partial(flask.g.api.get, "activity/about_me",
        params=params, version="i"))


@app.route("/activity")
@decorators.login_required
@decorators.templated("timeline.html")
def activity_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    return timeline("Activity", functools.partial(flask.g.api.get, "activity/by_friends",
        params=params, version="i"))


@app.route("/search")
@decorators.templated("timeline.html")
def search_tweets():
    return {}