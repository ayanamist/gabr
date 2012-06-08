import flask

from application import app
from ..lib import decorators
from ..lib import render
from ..lib import twitter


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    keep_max_id = bool(flask.request.args.get("keep_max_id", False))
    data = {
        "title": "Home",
        "tweets": tuple(),
        }
    params = dict()
    for access_param in ("max_id", "page", "since_id", "count"):
        param = flask.request.args.get(access_param)
        if param:
            try:
                param = int(param, 10)
                params[access_param] = param
            except ValueError:
                pass

    try:
        home_result = flask.g.api.get_home_timeline(**params)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        max_id = flask.request.args.get("max_id")
        if not keep_max_id and max_id:
            for i, tweet in enumerate(home_result):
                if tweet["id_str"] == max_id:
                    del home_result[i]
        data["tweets"] = render.prerender_timeline(home_result)
    return data


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline_ex.html")
def connect_timeline():
    return {
        "title": "Connect",
        }


@app.route("/user/<screen_name>/tweets")
@decorators.templated("timeline.html")
def user_timeline(screen_name):
    return {
        "title": "%s's tweets" % screen_name
    }


@app.route("/search")
@decorators.templated("timeline.html")
def search_tweets():
    return {}