from __future__ import absolute_import

import flask

from application.models import twitter


@flask.current_app.before_request
def before_request():
    flask.session.permanent = True

    flask.g.screen_name = flask.session.get("screen_name")
    oauth_token = flask.session.get("oauth_token")
    oauth_token_secret = flask.session.get("oauth_token_secret")
    flask.g.api = twitter.API(flask.current_app.config["CONSUMER_KEY"], flask.current_app.config["CONSUMER_SECRET"])
    if oauth_token and oauth_token_secret:
        flask.g.api.bind_auth(oauth_token, oauth_token_secret)



