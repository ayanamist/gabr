import email
import time

import flask
import jinja2

from . import indicesreplace

def prerender_timeline(timeline_json):
    return [prerender_tweet(x) for x in timeline_json]


def prerender_tweet(tweet_json):
    tweet_json = prerender_retweet(tweet_json)
    tweet_json = prerender_timestamp(tweet_json)
    tweet_json = prerender_entities(tweet_json)
    return tweet_json


def prerender_retweet(tweet_json):
    retweeted_status = tweet_json.get('retweeted_status')
    if retweeted_status:
        retweet = tweet_json
        tweet_json = retweeted_status
        tweet_json['retweeted'] = retweet
        del tweet_json['retweeted']['retweeted_status']
    return tweet_json


def prerender_timestamp(tweet_json):
    unix_timestamp = time.mktime(email.utils.parsedate(tweet_json['created_at']))
    tweet_json["timestamp"] = unix_timestamp
    unix_timestamp += 28800 # GMT+8
    t = time.gmtime(unix_timestamp)
    now_t = time.gmtime()
    date_fmt = "%m-%d %H:%M:%S"
    if now_t.tm_year != t.tm_year:
        date_fmt = "%Y-" + date_fmt
    tweet_json["created_at_fmt"] = time.strftime(date_fmt, t)
    return tweet_json


def prerender_entities(tweet_json):
    tweet_json["text_raw"] = tweet_json["text"]

    entities = tweet_json.get("entities")
    if not entities:
        return tweet_json
    new_text = indicesreplace.IndicesReplace(tweet_json["text_raw"])

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
            tweet_json["highlight"] = True

    tweet_json["text"] = unicode(new_text)
    return tweet_json


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