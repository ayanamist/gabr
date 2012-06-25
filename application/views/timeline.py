import flask

from application import app
from ..lib import decorators
from ..lib import twitter


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
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
        result = flask.g.api.get_home_timeline(**params)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        max_id = flask.request.args.get("max_id")
        if max_id:
            for i, tweet in enumerate(result):
                if tweet["id_str"] == max_id:
                    del result[i]
        data["tweets"] = result
    return data


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline_ex.html")
def connect_timeline():
    return {
        "title": "Connect",
        }


@app.route("/activity")
@decorators.login_required
@decorators.templated("timeline_ex.html")
def activity_timeline():
    return {
        "title": "Activity",
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