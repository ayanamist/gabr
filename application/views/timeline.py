import functools

import flask
import twython

from .. import utils
from ..utils import decorators
from application import app

def timeline(title, api_func):
    data = {
        "title": title,
        "results": list(),
        }
    try:
        results = api_func()
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        data["results"] = results
    return data


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Home", functools.partial(flask.g.api.getHomeTimeline, **params))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    return data


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline.html")
def connect_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Connect", functools.partial(flask.g.api.get, "activity/about_me",
        params=params, version="i"))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    return data


@app.route("/activity")
@decorators.login_required
@decorators.templated("timeline.html")
def activity_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Activity", functools.partial(flask.g.api.get, "activity/by_friends",
        params=params, version="i"))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    return data


@app.route("/search")
@decorators.login_required
@decorators.templated("timeline.html")
def search_tweets():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Search", functools.partial(flask.g.api.search, **params))
    if data["results"]:
        results = data["results"] = utils.remove_status_by_id(data["results"]["results"], params.get("max_id"))
        for result in results:
            result["user"] = {
                "screen_name": result["from_user"],
                "id": result["from_user_id"],
                "id_str": result["from_user_id_str"],
                "profile_image_url": result["profile_image_url"],
                }
    return data