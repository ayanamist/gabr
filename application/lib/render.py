import email
import time

import flask
import jinja2

from . import indicesreplace

def prerender_timeline(timeline_json):
    return [prerender_tweet(x) for x in timeline_json]


def prerender_tweet(tweet_json):
    tweet_json = prerender_retweet(tweet_json)
    if "retweet" in tweet_json:
        tweet_json["retweet"] = prerender_timestamp(tweet_json["retweet"])
    tweet_json = prerender_timestamp(tweet_json)
    tweet_json = prerender_entities(tweet_json)
    return tweet_json


def prerender_retweet(json_data):
    retweeted_status = json_data.get("retweeted_status")
    if retweeted_status:
        retweet = json_data
        json_data = retweeted_status
        json_data["retweet"] = retweet
        del json_data["retweet"]["retweeted_status"]
    return json_data


def prerender_timestamp(json_data):
    unix_timestamp = time.mktime(email.utils.parsedate(json_data["created_at"]))
    json_data["timestamp"] = unix_timestamp
    unix_timestamp += 28800 # GMT+8
    t = time.gmtime(unix_timestamp)
    now_t = time.gmtime()
    date_fmt = "%m-%d %H:%M:%S"
    if now_t.tm_year != t.tm_year:
        date_fmt = "%Y-" + date_fmt
    json_data["created_at_fmt"] = time.strftime(date_fmt, t)
    return json_data


def prerender_entities(json_data):
    json_data["text_raw"] = json_data["text"]

    entities = json_data.get("entities")
    if not entities:
        return json_data
    new_text = indicesreplace.IndicesReplace(json_data["text_raw"])

    medias = entities.get("media", list())
    for media in medias:
        start, stop = media["indices"]
        data = {
            "url": media["expanded_url"],
            "text": media["display_url"],
            }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">%(text)s</a>" % data)
        media["preview_url"] = "%s:thumb" % media["media_url"]

    hashtags = entities.get("hashtags", list())
    for hashtag in hashtags:
        start, stop = hashtag["indices"]
        data = {
            "url": "%s?q=%s" % (flask.url_for("search_tweets"), hashtag["text"]),
            "text": hashtag["text"],
            }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">#%(text)s</a>" % data)

    urls = entities.get("urls", list())
    for url in urls:
        start, stop = url["indices"]
        data = {
            "url": url["expanded_url"],
            "text": url["display_url"],
            }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">%(text)s</a>" % data)

    user_mentions = entities.get("user_mentions", list())
    for user_mention in user_mentions:
        start, stop = user_mention["indices"]
        data = {
            "url": flask.url_for("user", screen_name=user_mention["screen_name"]),
            "title": user_mention["name"],
            "text": user_mention["screen_name"],
            }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\" title=\"%(title)s\">@%(text)s</a>" % data)
        if user_mention["screen_name"] == flask.g.screen_name:
            json_data["highlight"] = True

    json_data["text"] = unicode(new_text)
    return json_data


@jinja2.environmentfilter
def do_item(environment, obj, name):
    try:
        name = str(name)
    except UnicodeError:
        pass
    else:
        try:
            value = obj[name]
        except (TypeError, KeyError):
            pass
        else:
            return value
    return environment.undefined(obj=obj, name=name)

jinja2.filters.FILTERS["item"] = do_item