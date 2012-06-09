import flask

from application import app
from ..lib import decorators
from ..lib import render
from ..lib import twitter

@app.route("/status/<int:id>")
@decorators.templated("timeline.html")
def status(id):
    pass


@app.route("/status/<int:id>/reply", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_reply.html")
def status_reply(id):
    return {}


@app.route("/status/<int:id>/replyall")
@decorators.login_required
@decorators.templated("status_reply.html")
def status_replyall(id):
    return {}


@app.route("/status/<int:id>/retweet", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_retweet.html")
def status_retweet(id):
    return {}


@app.route("/status/<int:id>/favorite")
@decorators.login_required
@decorators.templated("tweets.html")
def status_favorite(id):
    data = {
        "title": "Favorite",
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.create_favorite(id)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Created favorite successfully!")
        result["favorited"] = True # fucking twitter won't mark it as favorited.
        data["tweets"] = [render.prerender_tweet(result)]
    return data


@app.route("/status/<int:id>/unfavorite")
@decorators.login_required
@decorators.templated("tweets.html")
def status_unfavorite(id):
    data = {
        "title": "Unfavorite",
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.destroy_favorite(id)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Destroyed favorite successfully!")
        result["favorited"] = False # fucking twitter won't mark it as not favorited.
        data["tweets"] = [render.prerender_tweet(result)]
    return data


@app.route("/status/<int:id>/delete")
@decorators.login_required
@decorators.templated("tweets.html")
def status_delete(id):
    data = {
        "title": "Unfavorite",
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.destroy_status(id)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Destroyed status successfully!")
        result["deleted"] = True
        data["tweets"] = [render.prerender_tweet(result)]
    return data

