import email
import time

import flask
import jinja2

from . import indicesreplace

def prerender_timeline(timeline_json):
    return [prerender_tweet(x) for x in timeline_json]


def screen_name_exists(screen_name, entities):
    for user_mention in entities.get("user_mentions", list()):
        if user_mention["screen_name"] == screen_name:
            return True
    return False


def prerender_tweet(tweet_json):
    tweet_json = prerender_retweet(tweet_json)
    if "retweet" in tweet_json:
        tweet_json["retweet"] = prerender_tweet(tweet_json["retweet"])
    tweet_json["timestamp"] = prerender_timestamp(tweet_json["created_at"])
    tweet_json["created_at_fmt"] = prerender_created_at(tweet_json["created_at"])
    tweet_json["text_raw"] = tweet_json["text"]
    entities = tweet_json.get("entities")
    if entities:
        tweet_json["text"] = prerender_entities(tweet_json["text_raw"], entities)
        tweet_json["highlight"] = screen_name_exists(flask.g.screen_name, entities)
    return tweet_json


def prerender_retweet(json_data):
    retweeted_status = json_data.get("retweeted_status")
    if retweeted_status:
        retweet = json_data
        json_data = retweeted_status
        json_data["retweet"] = retweet
        del json_data["retweet"]["retweeted_status"]
    return json_data


def prerender_timestamp(created_at):
    return time.mktime(email.utils.parsedate(created_at))


def prerender_created_at(created_at):
    unix_timestamp = prerender_timestamp(created_at)
    unix_timestamp += 28800 # GMT+8
    t = time.gmtime(unix_timestamp)
    now_t = time.gmtime()
    date_fmt = "%m-%d %H:%M:%S"
    if now_t.tm_year != t.tm_year:
        date_fmt = "%Y-" + date_fmt
    return time.strftime(date_fmt, t)


def prerender_entities(text, entities):
    new_text = indicesreplace.IndicesReplace(text)
    new_text.highlight = False

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

    return unicode(new_text)


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