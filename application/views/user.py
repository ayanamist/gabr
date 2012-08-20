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
            days_delta = (time.time() - render.prerender_timestamp(result["created_at"])) // 86400
            data["user"]["tweets_per_day"] = "%.4g" % (result["statuses_count"] / days_delta) if days_delta > 0 else 0
        try:
            result = flask.g.api.showFriendships(source_screen_name=flask.g.screen_name,
                target_screen_name=data["user"]["screen_name"])
        except twitter.Error:
            pass
        else:
            source = result["relationship"]["source"]
            del source["id_str"]
            del source["id"]
            del source["screen_name"]
            data["user"].update(source)
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


@app.route("/user/<screen_name>/follow")
def user_follow(screen_name):
    try:
        result = flask.g.api.create_friendship(screen_name)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Following user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/unfollow")
def user_unfollow(screen_name):
    try:
        result = flask.g.api.destroy_friendship(screen_name)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unfollowed user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/block")
def user_block(screen_name):
    try:
        result = flask.g.api.create_block(screen_name)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Blocking user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/unblock")
def user_unblock(screen_name):
    try:
        result = flask.g.api.destroy_block(screen_name)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unblocked user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/reportspam")
def user_reportspam(screen_name):
    try:
        result = flask.g.api.report_spam(screen_name)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Reported user %s as spam." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))

