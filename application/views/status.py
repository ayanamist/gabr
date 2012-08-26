import operator

import flask
import twython

from ..utils import decorators
from ..utils import render
from application import app

@app.route("/post", methods=["GET", "POST"])
@decorators.login_required
def status_post():
    data = dict()
    if flask.request.method == "POST":
        status_text = flask.request.form.get("status", "")
        try:
            retweet_id = flask.request.form.get("retweet_id")
            if "retweet" in flask.request.form and retweet_id:
                result = flask.g.api.reTweet(id=retweet_id, include_entities=1)
            else:
                in_reply_to_id = flask.request.form.get("in_reply_to_id")
                result = flask.g.api.postUpdate(status_text, in_reply_to_id=in_reply_to_id, include_entities=1)
        except twython.TwythonError, e:
            flask.flash("Post error: %s" % str(e))
            data["preset_status"] = status_text
        else:
            data["title"] = "New Tweet"
            return flask.render_template("redirect.html", url=flask.url_for("status", id=result["id"]))
    data["title"] = "What's happening?"
    return flask.render_template("status_post.html", **data)


@app.route("/status/<int:id>")
@decorators.templated("results.html")
def status(id):
    data = {
        "title": "Status %d" % id,
        "tweets": list(),
        }
    try:
        origin_status = flask.g.api.showStatus(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        tweets = list()
        try:
            related_result = flask.g.api.get("related_results/show/%d" % id, include_entities=1)
        except twython.TwythonError, e:
            flask.flash("Get related status error: %s" % str(e))
        else:
            if related_result:
                last_conversation_role = 'Ancestor' # possible value: Ancestor, Descendant, Fork
                related_result = related_result[0]['results']
                for result in related_result:
                    if result['kind'] == 'Tweet':
                        conversation_role = result['annotations']['ConversationRole']
                        if conversation_role != last_conversation_role:
                            tweets.insert(0, origin_status)
                            origin_status = None
                            last_conversation_role = conversation_role
                        tweets.insert(0, result["value"])
        if origin_status:
            tweets.insert(0, origin_status)
        previous_ids = set(x["id"] for x in tweets)
        for i, status in enumerate(tweets):
            if "retweeted_status" not in status:
                current_id = status["in_reply_to_status_id"]
            else:
                current_id = status["retweeted_status"]["in_reply_to_status_id"]
            if current_id and current_id not in previous_ids:
                try:
                    status = flask.g.api.showStatus(id=current_id, include_entities=1)
                except twython.TwythonError:
                    pass
                else:
                    tweets.insert(i + 1, status)
                    previous_ids.add(status["id"])
        first_short = tweets[0]['id_str'] == id
        while len(tweets) <= 4 or first_short:
            first_short = False
            status = tweets[0]
            if status['in_reply_to_status_id_str']:
                current_id = status['in_reply_to_status_id_str']
                try:
                    status = flask.g.api.showStatus(id=current_id, include_entities=1)
                except twython.TwythonError:
                    break
            else:
                break
            if 'retweeted_status' in status and status["retweeted_status"]["id"] not in previous_ids:
                tweets.append(status['retweeted_status'])
                previous_ids.add(status['retweeted_status']["id"])
            elif status["id"] not in previous_ids:
                tweets.append(status)
                previous_ids.add(status["id"])
        tweets.sort(key=operator.itemgetter("id"))
        data["tweets"] = tweets
    return data


@app.route("/status/<int:id>/reply", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_post.html")
def status_reply(id):
    data = {
        "title": "Reply",
        }
    try:
        result = flask.g.api.showStatus(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["preset_status"] = "@%s " % result["user"]["screen_name"]
        data["in_reply_to_id"] = id
        data["in_reply_to_status"] = render.prerender_tweet(result)
    return data


@app.route("/status/<int:id>/replyall")
@decorators.login_required
@decorators.templated("status_post.html")
def status_replyall(id):
    data = {
        "title": "Reply to All",
        }
    try:
        result = flask.g.api.showStatus(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["in_reply_to_status"] = render.prerender_tweet(result)
        mentioned_screen_name = [result["user"]["screen_name"]]
        entities = result.get("entities")
        if entities:
            for user_mention in entities.get("user_mentions", list()):
                if user_mention["screen_name"] not in mentioned_screen_name:
                    mentioned_screen_name.append(user_mention["screen_name"])
        if flask.g.screen_name in mentioned_screen_name and len(mentioned_screen_name) > 1:
            mentioned_screen_name.remove(flask.g.screen_name)
        data["preset_status"] = "%s " % " ".join("@%s" % x for x in mentioned_screen_name)
    return data


@app.route("/status/<int:id>/retweet", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_post.html")
def status_retweet(id):
    data = {
        "title": "Retweet",
        }
    try:
        result = flask.g.api.showStatus(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["preset_status"] = "RT @%s: %s" % (result["user"]["screen_name"], result["text"])
        data["retweet_id"] = id
        data["retweet"] = True
    return data


@app.route("/status/<int:id>/favorite")
@decorators.login_required
@decorators.templated("results.html")
def status_favorite(id):
    data = {
        "title": "Favorite",
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.createFavorite(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Create favorite error: %s" % str(e))
    else:
        flask.flash("Created favorite successfully!")
        result["favorited"] = True # fucking twitter won't mark it as favorited.
        data["results"] = [render.prerender_tweet(result)]
    return data


@app.route("/status/<int:id>/unfavorite")
@decorators.login_required
@decorators.templated("results.html")
def status_unfavorite(id):
    data = {
        "title": "Unfavorite",
        "tweets": tuple(),
        }
    try:
        result = flask.g.api.destroyFavorite(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Destroy favorite error: %s" % str(e))
    else:
        flask.flash("Destroyed favorite successfully!")
        result["favorited"] = False # fucking twitter won't mark it as not favorited.
        data["results"] = [render.prerender_tweet(result)]
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
        result = flask.g.api.destroyStatus(id=id, include_entities=1)
    except twython.TwythonError, e:
        flask.flash("Destroy status error: %s" % str(e))
    else:
        flask.flash("Destroyed status successfully!")
        result["deleted"] = True
        data["results"] = [render.prerender_tweet(result)]
    return flask.render_template("results.html", **data)

