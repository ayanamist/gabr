import time

import flask
import twython

from .. import utils
from application.libs import render
from ..utils import decorators
from application import app

@app.route("/user/<screen_name>")
@decorators.login_required
@decorators.templated("user_show.html")
def user(screen_name):
    data = {
        "results": list(),
        }
    if not flask.request.args:
        data["title"] = "User %s" % screen_name
        try:
            result = flask.g.api.showUser(screen_name=screen_name)
        except twython.TwythonError, e:
            flask.flash("Can not show user %s: %s" % (screen_name, str(e)))
        else:
            data["user"] = result
            days_delta = (time.time() - render.prerender_timestamp(result["created_at"])) // 86400
            data["user"]["tweets_per_day"] = "%.4g" % (result["statuses_count"] / days_delta) if days_delta > 0 else 0
        try:
            result = flask.g.api.showFriendship(source_screen_name=flask.g.screen_name,
                target_screen_name=data["user"]["screen_name"])
        except twython.TwythonError:
            pass
        else:
            source = result["relationship"]["source"]
            del source["id_str"]
            del source["id"]
            del source["screen_name"]
            data["user"].update(source)
    else:
        data["title"] = "User %s Timeline" % screen_name
    params = utils.parse_params()
    params["include_entities"] = 1
    try:
        tweets_result = flask.g.api.getUserTimeline(screen_name=screen_name, **params)
    except twython.TwythonError, e:
        flask.flash("Can not get timeline: %s" % str(e))
    else:
        data["results"] = utils.remove_status_by_id(tweets_result, flask.request.args.get("max_id"))
    data["next_page_url"] = utils.build_next_page_url(data["results"], flask.request.args.to_dict())
    return data


@app.route("/user/<screen_name>/follow")
@decorators.login_required
def user_follow(screen_name):
    try:
        result = flask.g.api.createFriendship(screen_name=screen_name)
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Following user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/unfollow")
@decorators.login_required
def user_unfollow(screen_name):
    try:
        result = flask.g.api.destroyFriendship(screen_name=screen_name)
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unfollowed user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/block")
@decorators.login_required
def user_block(screen_name):
    try:
        result = flask.g.api.createBlock(screen_name=screen_name)
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Blocking user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/unblock")
@decorators.login_required
def user_unblock(screen_name):
    try:
        result = flask.g.api.destroyBlock(screen_name=screen_name)
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Unblocked user %s." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))


@app.route("/user/<screen_name>/reportspam")
@decorators.login_required
def user_reportspam(screen_name):
    try:
        result = flask.g.api.reportSpam(screen_name=screen_name)
    except twython.TwythonError, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Reported user %s as spam." % result["screen_name"])
    return flask.redirect(flask.url_for("user", screen_name=screen_name))

