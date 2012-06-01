import httplib
import urllib

import flask

from application import app
from ..lib import decorators
from ..lib import oauth
from ..lib import urlfetch

def _get_oauth_handler():
    oauth_token = flask.session.get("oauth_token")
    oauth_token_secret = flask.session.get("oauth_token_secret")
    if oauth_token and oauth_token_secret:
        oauth_handler = oauth.OAuthHandler(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
        oauth_handler.set_access_token(oauth_token, oauth_token_secret)
        return oauth_handler


@app.route("/")
@decorators.login_required
@decorators.templated("timeline.html")
def home_timeline():
    oauth_handler = _get_oauth_handler()

    data = {
        "title": "Home",
        "tweets": tuple(),
        "keep_max_id": bool(flask.request.args.get("keep_max_id", False)),
        }

    params = {
        "include_entities": 1,
        "include_rts": 1,
        }
    for access_param in ("max_id", "page", "since_id", "count"):
        param = flask.request.args.get(access_param, 0)
        try:
            param = int(param, 10)
        except ValueError:
            param = None
        if param:
            params[access_param] = param

    url = "https://api.twitter.com/1/statuses/home_timeline.json?%s" % urllib.urlencode(params)
    try:
        home_result = urlfetch.twitter_fetch(url=url, oauth_handler=oauth_handler)
    except urlfetch.Error, e:
        flask.flash("Network Error: %s" % str(e))
        return data
    if home_result.status_code != httplib.OK:
        if home_result.content_json and "error" in home_result.content_json:
            error_message = home_result.content_json["error"]
        else:
            error_message = "Twitter Internal Server Error"
        flask.flash("Error %d: %s" % (home_result.status_code, error_message))
        return data
    data["tweets"] = home_result.content_json
    return data


@app.route("/connect")
@decorators.login_required
@decorators.templated("timeline_ex.html")
def connect_timeline():
    return {
        "title": "Connect",
        }


@app.route("/user/<screen_name>/tweets")
@decorators.templated("timeline.html")
def user_timeline(screen_name):
    return {
        "title": "%s's tweets" % screen_name
    }