import email.utils
import time

import flask

from application import app
from ..lib import decorators
from ..lib import render
from ..lib import twitter

@app.route("/user/<screen_name>")
@decorators.templated("user_show.html")
def user(screen_name):
    data = dict()
    if not flask.request.args:
        data["title"] = "User %s" % screen_name
        try:
            result = flask.g.api.get_user(screen_name)
        except twitter.Error, e:
            flask.flash("Can not lookup user %s: %s" % (screen_name, str(e)))
        else:
            data["user"] = result
            data["user"]["created_at_fmt"] = render.prerender_timestamp(result["created_at"])
            days_delta = (time.time() - time.mktime(email.utils.parsedate(result["created_at"]))) // 86400
            data["user"]["tweets_per_day"] = "%.4g" % (result["statuses_count"] / days_delta)
    else:
        data["title"] = "User %s Timeline" % screen_name

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
        tweets_result = flask.g.api.get_user_timeline(screen_name=screen_name, **params)
    except twitter.Error, e:
        data["results"] = list()
        flask.flash("Can not get timeline: %s" % str(e))
    else:
        max_id = flask.request.args.get("max_id")
        if max_id:
            for i, tweet in enumerate(tweets_result):
                if tweet["id_str"] == max_id:
                    del tweets_result[i]
        data["results"] = tweets_result
    return data