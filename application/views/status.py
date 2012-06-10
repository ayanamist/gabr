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
        try:
            retweet_id = flask.request.form.get("retweet_id")
            if retweet_id:
                result = flask.g.api.create_retweet(retweet_id)
            else:
                in_reply_to_id = flask.request.form.get("in_reply_to_id")
                result = flask.g.api.post_update(flask.request.form.get("status"), in_reply_to_id)
        except twitter.Error, e:
            data["title"] = "Post Error"
            flask.flash("Post error: %s" % str(e))
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
        flask.flash("Get status error: %s" % str(e))
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
@decorators.templated("status_post.html")
def status_reply(id):
    data = {
        "title": "Reply",
        }
    try:
        result = flask.g.api.get_status(id)
    except twitter.Error, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["preset_status"] = "@%s " % result["user"]["screen_name"]
        data["in_reply_to_id"] = id
        data["word_count"] = twitter.CHARACTER_LIMIT - len(data["preset_status"])
    return data


@app.route("/status/<int:id>/replyall")
@decorators.login_required
@decorators.templated("status_post.html")
def status_replyall(id):
    data = {
        "title": "Reply to All",
        }
    try:
        result = flask.g.api.get_status(id)
    except twitter.Error, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        mentioned_screen_name = [result["user"]["screen_name"]]
        entities = result.get("entities")
        if entities:
            for user_mention in entities.get("user_mentions", list()):
                if user_mention["screen_name"] not in mentioned_screen_name:
                    mentioned_screen_name.append(user_mention["screen_name"])
        if flask.g.screen_name in mentioned_screen_name and len(mentioned_screen_name) > 1:
            mentioned_screen_name.remove(flask.g.screen_name)
        data["preset_status"] = "%s " % " ".join("@%s" % x for x in mentioned_screen_name)
        data["in_reply_to_id"] = id
        data["word_count"] = twitter.CHARACTER_LIMIT - len(data["preset_status"])
    return data


@app.route("/status/<int:id>/retweet", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_post.html")
def status_retweet(id):
    data = {
        "title": "Retweet",
        }
    try:
        result = flask.g.api.get_status(id)
    except twitter.Error, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["preset_status"] = "RT @%s: %s" % (result["user"]["screen_name"], result["text"])
        data["word_count"] = twitter.CHARACTER_LIMIT - len(data["preset_status"])
        data["retweet_id"] = id
        data["retweet"] = True
    return data


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
        flask.flash("Create favorite error: %s" % str(e))
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
        flask.flash("Destroy favorite error: %s" % str(e))
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
        flask.flash("Destroy status error: %s" % str(e))
    else:
        flask.flash("Destroyed status successfully!")
        result["deleted"] = True
        data["tweets"] = [render.prerender_tweet(result)]
    return flask.render_template("tweets.html", **data)

