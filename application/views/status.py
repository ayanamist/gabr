import operator

import flask

from application import app
from ..lib import decorators
from ..lib import render
from ..lib import twitter

@app.route("/post", methods=["GET", "POST"])
@decorators.login_required
def status_post():
    data = dict()
    if flask.request.method == "POST":
        in_reply_to_id = flask.request.form.get("in_reply_to_id")
        if not in_reply_to_id:
            in_reply_to_id = None
        try:
            result = flask.g.api.post_update(flask.request.form.get("status"), in_reply_to_id)
        except twitter.Error, e:
            data["title"] = "Post Error"
            flask.flash("Post Error: %s" % str(e))
            data["tweets"] = list()
        else:
            data["title"] = "New Tweet"
            data["tweets"] = [render.prerender_tweet(result)]
        return flask.render_template("tweets.html", **data)
    data["title"] = "What's happening?"
    return flask.render_template("status_post.html", **data)


@app.route("/status/<int:id>")
@decorators.templated("tweets.html")
def status(id):
    data = {
        "title": "Status %d" % id,
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.get_status(id)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        result["highlight"] = True
        data["tweets"] = [result]
        related_results = list()
        try:
            result = flask.g.api.get_related_results(id)
            if result:
                related_results = result[0]['results']
        except twitter.Error:
            pass
        orig_index = 0
        for related_result in related_results:
            if related_result['kind'] == 'Tweet':
                conversation_role = related_result['annotations']['ConversationRole']
                if conversation_role == "Ancestor":
                    data["tweets"].insert(orig_index, related_result["value"])
                    orig_index += 1
                else: # possible value: Descendant, Fork
                    data["tweets"].append(related_result["value"])
        status_id = data["tweets"][0].get("in_reply_to_status_id")
        while orig_index < 3 and status_id:
            try:
                result = flask.g.api.get_status(status_id)
            except twitter.NotFoundError:
                data["tweets"][0]["in_reply_to_status_id"] = None
                break
            except twitter.Error:
                break
            else:
                data["tweets"].insert(0, result)
                status_id = result.get("in_reply_to_status_id")
                orig_index += 1
        data["tweets"] = render.prerender_timeline(data["tweets"])
        # Since twitter will return misordered forks, i think sorted by timestamp will solve this problem.
        data["tweets"].sort(key=operator.itemgetter("timestamp"))
    return data


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


@app.route("/status/<int:id>/delete", methods=['GET', 'POST'])
@decorators.login_required
def status_delete(id):
    data = {
        "title": "Delete",
        "tweets": tuple(),
        }
    if flask.request.method == "GET":
        data["status_id"] = id
        return flask.render_template("status_delete.html", **data)
    try:
        result = flask.g.api.destroy_status(id)
    except twitter.Error, e:
        flask.flash("Error: %s" % str(e))
    else:
        flask.flash("Destroyed status successfully!")
        result["deleted"] = True
        data["tweets"] = [render.prerender_tweet(result)]
    return flask.render_template("tweets.html", **data)

