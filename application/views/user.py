from __future__ import absolute_import

import time

import flask

from application import utils
from application.libs import render
from application.models import twitter
from application.utils import decorators


@decorators.login_required
@decorators.templated("user_show.html")
def user(screen_name):
    data = {
        "title": "User %s" % screen_name,
        "results": [],
    }
    if not flask.request.args:
        try:
            result = flask.g.api.get("users/show", screen_name=screen_name).json()
        except twitter.Error as e:
            flask.flash("Can not show user %s: %s" % (screen_name, str(e)))
            return data
        data["user"] = result
        days_delta = (time.time() - render.prerender_timestamp(result["created_at"])) // 86400
        data["user"]["tweets_per_day"] = "%.4g" % (result["statuses_count"] / days_delta) if days_delta > 0 else 0
        try:
            result = flask.g.api.get("friendships/show", source_screen_name=flask.g.screen_name,
                                     target_screen_name=data["user"]["screen_name"]).json()
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
    params = flask.request.args.to_dict()
    try:
        tweets_result = flask.g.api.get("statuses/user_timeline", screen_name=screen_name, **params).json()
    except twitter.Error as e:
        flask.flash("Can not get timeline: %s" % str(e))
    else:
        data["results"] = utils.remove_status_by_id(tweets_result, flask.request.args.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict())
    return data


@decorators.login_required
def user_follow(screen_name):
    try:
        result = flask.g.api.post("friendships/create", screen_name=screen_name).json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Following user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@decorators.login_required
def user_unfollow(screen_name):
    try:
        result = flask.g.api.post("friendships/destroy", screen_name=screen_name).json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unfollowed user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@decorators.login_required
def user_block(screen_name):
    try:
        result = flask.g.api.post("blocks/create", screen_name=screen_name).json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Blocking user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@decorators.login_required
def user_unblock(screen_name):
    try:
        result = flask.g.api.post("blocks/destroy", screen_name=screen_name).json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unblocked user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@decorators.login_required
def user_reportspam(screen_name):
    try:
        result = flask.g.api.post("users/report_spam", screen_name=screen_name).json()
    except twitter.Error as e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Reported user %s as spam." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))
