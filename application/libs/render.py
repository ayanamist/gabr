from __future__ import absolute_import

import email
import time
import urllib

import flask

from application import utils
from application.libs import indicesreplace
from application.libs import preview

preview_builders = [getattr(preview, f) for f in dir(preview) if f.startswith("media_")]


def screen_name_exists(screen_name, entities):
    for user_mention in entities.get("user_mentions", list()):
        if user_mention["screen_name"] == screen_name:
            return True
    return False


def prerender_tweet(tweet_json):
    tweet_json = prerender_retweet(tweet_json)
    if "retweet" in tweet_json:
        tweet_json["retweet"] = prerender_tweet(tweet_json["retweet"])
    tweet_json["text_raw"] = tweet_json["text"]
    entities = tweet_json.get("entities")
    if entities:
        tweet_json["text"] = prerender_tweet_entities(tweet_json["text_raw"], tweet_json)
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


def render_created_at(created_at):
    unix_timestamp = prerender_timestamp(created_at)
    unix_timestamp += 28800  # GMT+8
    t = time.gmtime(unix_timestamp)
    now_t = time.gmtime()
    date_fmt = "%m-%d %H:%M:%S"
    if now_t.tm_year != t.tm_year:
        date_fmt = "%Y-" + date_fmt
    return time.strftime(date_fmt, t)


def get_preview_url(url):
    for func in preview_builders:
        result = func(url)
        if result:
            return result


def prerender_user_entities(user_json):
    entities = user_json.get("entities")
    if entities and isinstance(entities, dict):
        for key, value in entities.iteritems():
            old_content = user_json.get(key)
            urls = value.get("urls")
            if old_content and urls:
                new_content = indicesreplace.IndicesReplace(old_content)
                for url in urls:
                    if "display_url" not in url or not url["display_url"]:
                        url["display_url"] = url.get("url")
                    if "expanded_url" not in url or not url["expanded_url"]:
                        url["expanded_url"] = url.get("url")
                    if url.get("expanded_url"):
                        start, stop = url["indices"]
                        if not url["display_url"]:
                            url["display_url"] = url["expanded_url"]
                        new_content.replace_indices(start, stop, "<a href=\"%(expanded_url)s\">%(display_url)s</a>" % url)
                user_json[key] = unicode(new_content)

    return user_json


def prerender_tweet_entities(text, tweet_json):
    entities = tweet_json["entities"]
    if not isinstance(entities, dict):
        return text
    extended_entities = tweet_json.get("extended_entities")
    new_text = indicesreplace.IndicesReplace(text)
    new_text.highlight = False

    hashtags = entities.get("hashtags", list())
    for hashtag in hashtags:
        start, stop = hashtag["indices"]
        data = {
            "url": "%s?q=%%23%s" % (utils.abs_url_for("search_tweets"), urllib.quote(hashtag["text"].encode("UTF8"))),
            "text": hashtag["text"],
        }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">#%(text)s</a>" % data)

    user_mentions = entities.get("user_mentions", list())
    for user_mention in user_mentions:
        start, stop = user_mention["indices"]
        data = {
            "url": utils.abs_url_for("user", screen_name=user_mention["screen_name"]),
            "title": user_mention["name"],
            "text": user_mention["screen_name"],
        }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\" title=\"%(title)s\">@%(text)s</a>" % data)

    if "media" not in entities:
        entities["media"] = list()
    for media in entities["media"]:
        start, stop = media["indices"]
        data = {
            "url": media["expanded_url"],
            "text": media["display_url"],
        }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">%(text)s</a>" % data)
        media["preview_url"] = "%s:small" % media["media_url_https"]
        media["original_url"] = "%s:large" % media["media_url_https"]

    # support twitter new multiple picture in same tweet
    if extended_entities and isinstance(extended_entities, dict) and extended_entities["media"]:
        entities["media"] = extended_entities["media"]
        for media in entities["media"]:
            media["preview_url"] = "%s:small" % media["media_url_https"]
            media["original_url"] = "%s:large" % media["media_url_https"]

    urls = entities.get("urls", list())
    for url in urls:
        preview_urls = get_preview_url(url["expanded_url"])
        if preview_urls:
            url["preview_url"], url["original_url"] = preview_urls
            entities["media"].append(url)
        start, stop = url["indices"]
        data = {
            "url": url["expanded_url"],
            "text": url["display_url"],
        }
        new_text.replace_indices(start, stop, "<a href=\"%(url)s\">%(text)s</a>" % data)

    return unicode(new_text)
