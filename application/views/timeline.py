from __future__ import absolute_import

import functools
import urllib

import flask

from application import app
from application import utils
from application.models import twitter
from application.utils import decorators


def timeline(title, api_func):
    data = {
        "title": title,
        "results": list(),
    }
    try:
        results = api_func().json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        data["results"] = results
    return data


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    params = utils.parse_params()
    data = timeline("Home",
                    functools.partial(flask.g.api.request,
                                      method="GET",
                                      endpoint="statuses/home_timeline",
                                      params=params))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict())
    return data


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline.html")
def connect_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Connect",
                    functools.partial(flask.g.api.request,
                                      method="GET",
                                      endpoint="%s/i/activity/about_me.json" % twitter.BASE_URL,
                                      params=params))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict(),
                                                      key_name="max_position")
    return data


@app.route("/activity")
@decorators.login_required
@decorators.templated("timeline.html")
def activity_timeline():
    params = utils.parse_params()
    params["include_entities"] = 1
    data = timeline("Activity",
                    functools.partial(flask.g.api.request,
                                      method="GET",
                                      endpoint="%s/i/activity/by_friends.json" % twitter.BASE_URL,
                                      params=params))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict(),
                                                      key_name="max_position")
    return data


@app.route("/search")
@decorators.login_required
@decorators.templated("timeline.html")
def search_tweets():
    params = utils.parse_params()
    params["q"] = urllib.unquote(params["q"]).encode("utf8")
    data = timeline("Search",
                    functools.partial(flask.g.api.request,
                                      method="GET",
                                      endpoint="search/tweets",
                                      params=params))
    if data["results"]:
        results = data["results"] = utils.remove_status_by_id(data["results"]["results"], params.get("max_id"))
        for result in results:
            result["user"] = {
                "screen_name": result["from_user"],
                "id": result["from_user_id"],
                "id_str": result["from_user_id_str"],
                "profile_image_url": result["profile_image_url"],
            }
    data["next_page_url"] = utils.build_next_page_url(data["results"], params)
    return data


@app.route("/user/<screen_name>/favorites")
@decorators.login_required
@decorators.templated("timeline.html")
def user_favorites(screen_name):
    params = utils.parse_params()
    data = timeline("%s Favorites" % screen_name,
                    functools.partial(flask.g.api.request,
                                      method="GET",
                                      endpoint="favorites/list",
                                      screen_name=screen_name,
                                      params=params))
    data["results"] = utils.remove_status_by_id(data["results"], params.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict())
    return data
