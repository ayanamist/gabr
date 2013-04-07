from __future__ import absolute_import

import base64
import operator

import flask


from application import app
from application.libs import render
from application.models import twitter
from application.utils import decorators


@app.route("/post", methods=["GET", "POST"])
@decorators.login_required
def status_post():
    data = dict()
    if flask.request.method == "POST":
        status_text = flask.request.form.get("status")
        if status_text:
            pic_file = flask.request.files.get("pic-file")
            try:
                retweet_id = flask.request.form.get("retweet_id")
                if "retweet" in flask.request.form and retweet_id:
                    result = flask.g.api.request("POST", "statuses/retweet/%s" % retweet_id).json()
                else:
                    in_reply_to_id = flask.request.form.get("in_reply_to_id")
                    kwargs = {
                        "status": status_text,
                    }
                    if in_reply_to_id:
                        kwargs["in_reply_to_status_id"] = in_reply_to_id
                    if pic_file:
                        url = "https://upload.twitter.com/1.1/statuses/update_with_media.json"
                        kwargs["media_data[]"] = base64.b64encode(pic_file.read())
                        result = flask.g.api.request("POST", url, **kwargs).json()
                    else:
                        result = flask.g.api.request("POST", "statuses/update", **kwargs).json()
            except twitter.Error as e:
                flask.flash("Post error: %s" % str(e))
                data["preset_status"] = status_text
            else:
                data["title"] = "New Tweet"
                return flask.redirect("%s#t%s" % (flask.url_for("status", status_id=result["id"]), result["id_str"]))
    data["title"] = "What's happening?"
    return flask.render_template("status_post.html", **data)


@app.route("/status/<status_id>")
@decorators.login_required
@decorators.templated("results.html")
def status(status_id):
    data = {
        "title": "Status %s" % status_id,
        "results": list(),
    }
    try:
        origin_status = flask.g.api.request("GET", "statuses/show/%s" % status_id).json()
    except twitter.Error as e:
        flask.flash("Get status error: %s" % str(e))
    else:
        origin_status["orig"] = True
        tweets = list()
        if origin_status and not origin_status["user"]["protected"]:
            try:
                related_result = flask.g.api.request("GET",
                                                     "%s/1/related_results/show/%s.json" % (twitter.BASE_URL, status_id),
                                                     include_entities=1).json()
            except twitter.Error as e:
                flask.flash("Get related status error: %s" % str(e))
            else:
                if related_result:
                    last_conversation_role = 'Ancestor'  # possible value: Ancestor, Descendant, Fork
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
                    status = flask.g.api.request("GET", "statuses/show/%s" % current_id).json()
                except twitter.Error:
                    pass
                else:
                    tweets.insert(i + 1, status)
                    previous_ids.add(status["id"])
        while len(tweets) <= 4:
            status = tweets[-1]
            if status['in_reply_to_status_id_str']:
                current_id = status['in_reply_to_status_id_str']
                try:
                    status = flask.g.api.request("GET", "statuses/show/%s" % current_id).json()
                except twitter.Error:
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
        data["results"] = tweets
    return data


@app.route("/status/<status_id>/reply", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_post.html")
def status_reply(status_id):
    data = {
        "title": "Reply",
    }
    try:
        result = flask.g.api.request("GET", "statuses/show/%s" % status_id).json()
    except twitter.Error as e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["preset_status"] = "@%s " % result["user"]["screen_name"]
        data["in_reply_to_id"] = status_id
        data["in_reply_to_status"] = render.prerender_tweet(result)
    return data


@app.route("/status/<status_id>/replyall")
@decorators.login_required
@decorators.templated("status_post.html")
def status_replyall(status_id):
    data = {
        "title": "Reply to All",
    }
    try:
        result = flask.g.api.request("GET", "statuses/show/%s" % status_id).json()
    except twitter.Error as e:
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


@app.route("/status/<status_id>/retweet", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_post.html")
def status_retweet(status_id):
    data = {
        "title": "Retweet",
    }
    try:
        result = flask.g.api.request("GET", "statuses/show/%s" % status_id).json()
    except twitter.Error as e:
        flask.flash("Get status error: %s" % str(e))
    else:
        data["retweet_status"] = result
        data["preset_status"] = "RT @%s: %s" % (result["user"]["screen_name"], result["text"])
    return data


@app.route("/status/<status_id>/favorite")
@decorators.login_required
@decorators.templated("results.html")
def status_favorite(status_id):
    data = {
        "title": "Favorite",
        "tweets": list(),
    }
    try:
        result = flask.g.api.request("POST", "favorites/create", {"id": status_id}).json()
    except twitter.Error as e:
        flask.flash("Create favorite error: %s" % str(e))
    else:
        flask.flash("Created favorite successfully!")
        result["favorited"] = True  # fucking twitter won't mark it as favorited.
        data["results"] = [result]
    return data


@app.route("/status/<status_id>/unfavorite")
@decorators.login_required
@decorators.templated("results.html")
def status_unfavorite(status_id):
    data = {
        "title": "Unfavorite",
        "tweets": list(),
    }
    try:
        result = flask.g.api.request("POST", "favorites/destroy", {"id": status_id}).json()
    except twitter.Error as e:
        flask.flash("Destroy favorite error: %s" % str(e))
    else:
        flask.flash("Destroyed favorite successfully!")
        result["favorited"] = False  # fucking twitter won't mark it as not favorited.
        data["results"] = [result]
    return data


@app.route("/status/<status_id>/delete", methods=['GET', 'POST'])
@decorators.login_required
def status_delete(status_id):
    data = {
        "title": "Delete",
        "tweets": list(),
    }
    if flask.request.method == "GET":
        data["status_id"] = status_id
        return flask.render_template("status_delete.html", **data)
    try:
        result = flask.g.api.request("POST", "statuses/destroy/%s" % status_id).json()
    except twitter.Error as e:
        flask.flash("Destroy status error: %s" % str(e))
    else:
        flask.flash("Destroyed status successfully!")
        result["deleted"] = True
        data["results"] = [result]
    return flask.render_template("results.html", **data)
