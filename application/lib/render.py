import email
import time

def prerender_timeline(timeline_json):
    return [prerender_tweet(x) for x in timeline_json]


def prerender_tweet(tweet_json):
    tweet_json = prerender_retweet(tweet_json)
    tweet_json = prerender_timestamp(tweet_json)
    return tweet_json


def prerender_retweet(tweet_json):
    retweeted_status = tweet_json.get('retweeted_status')
    if retweeted_status:
        tweet_json['retweeted_status'] = prerender_tweet(retweeted_status)
        retweet = tweet_json
        tweet_json = retweeted_status
        tweet_json['retweeted'] = retweet
        del tweet_json['retweeted']['retweeted_status']
    return tweet_json


def prerender_timestamp(tweet_json):
    unix_timestamp = time.mktime(email.utils.parsedate(tweet_json['created_at']))
    unix_timestamp += 28800 # GMT+8
    t = time.gmtime(unix_timestamp)
    now_t = time.gmtime()
    date_fmt = "%m-%d %H:%M:%S"
    if now_t.tm_year != t.tm_year:
        date_fmt = "%Y-" + date_fmt
    tweet_json["timestamp"] = time.strftime(date_fmt, t)
    return tweet_json
