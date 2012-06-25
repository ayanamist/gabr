import flask

from application import app
from ..lib import decorators
from ..lib import twitter

def timeline(title, api_func):
    data = {
        "title": title,
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
        result = api_func(**params)
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


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    return timeline("Home", flask.g.api.get_home_timeline)


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline.html")
def connect_timeline():
    return timeline("Connect", flask.g.api.get_connect)


@app.route("/activity")
@decorators.login_required
@decorators.templated("timeline.html")
def activity_timeline():
    return timeline("Activity", flask.g.api.get_activity)


@app.route("/search")
@decorators.templated("timeline.html")
def search_tweets():
    return {}