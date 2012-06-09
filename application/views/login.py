import urlparse

import flask

from application import app
from ..lib import decorators
from ..lib import oauth
from ..lib import twitter

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"

AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"

ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

@app.route("/login")
@decorators.templated()
def login():
    return {
        "title": "Login",
        }


@app.route("/oauth")
def oauth_login():
    # TODO: oauth lib accept callback url.
    callback_url = "%s%s" % (flask.request.host_url, flask.url_for("oauth_callback"))
    consumer = oauth.Consumer(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
    client = oauth.Client(consumer)
    resp = client.request(twitter.REQUEST_TOKEN_URL, parameters={"oauth_callback": callback_url})
    if resp:
        request_token = dict(urlparse.parse_qsl(resp))
        oauth_token = request_token.get("oauth_token")
        if oauth_token:
            redirect_url = "%s?oauth_token=%s" % (twitter.AUTHORIZATION_URL, oauth_token)
            return flask.redirect(redirect_url)
    flask.flash("OAuth error, please try again.")
    return flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback")
def oauth_callback():
    flask.session.permanent = True
    oauth_token = flask.request.args.get("oauth_token")
    oauth_verifier = flask.request.args.get("oauth_verifier")
    if oauth_token and oauth_verifier:
        consumer = oauth.Consumer(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
        token = oauth.Token(oauth_token)
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
        resp = client.request(twitter.ACCESS_TOKEN_URL, "POST")
        if resp:
            access_token = dict(urlparse.parse_qsl(resp))
            oauth_token = access_token.get("oauth_token")
            oauth_token_secret = access_token.get("oauth_token_secret")
            screen_name = access_token.get("screen_name")
            if oauth_token and oauth_token_secret and screen_name:
                flask.session["oauth_token"] = oauth_token
                flask.session["oauth_token_secret"] = oauth_token_secret
                flask.session["screen_name"] = screen_name
                return flask.redirect(flask.url_for("home_timeline"))
    flask.flash("OAuth error, please try again.")
    return flask.redirect(flask.url_for("login"))


@app.route("/logout")
def logout():
    flask.session.permanent = True
    flask.session["screen_name"] = ""
    flask.session["oauth_token"] = ""
    flask.session["oauth_token_secret"] = ""
    flask.g.screen_name = None
    flask.flash("Logout successfully!")
    return flask.redirect(flask.url_for("login"))