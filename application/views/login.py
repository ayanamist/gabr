import logging
import urlparse

import flask

from application import app
from ..lib import oauth
from ..lib import urlfetch

@app.route("/login/")
def login():
    data = {
        "title": "Login",
        }
    return flask.render_template("login.html", **data)


@app.route("/oauth/")
def oauth_login():
    consumer = oauth.OAuthConsumer(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
        callback="%s%s" % (flask.request.host_url, flask.url_for("oauth_callback")),
        http_url="https://api.twitter.com/oauth/request_token")
    oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
    url = oauth_request.to_url()
    try:
        resp = urlfetch.fetch(url).content
    except urlfetch.Error:
        resp = ""
    request_token = dict(urlparse.parse_qsl(resp))
    oauth_token = request_token.get("oauth_token")
    if oauth_token:
        return flask.redirect("https://api.twitter.com/oauth/authorize?oauth_token=%s" % oauth_token)
    flask.flash("OAuth error, please try again.")
    return flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback/")
def oauth_callback():
    flask.session.permanent = True
    oauth_token = flask.request.args.get("oauth_token")
    oauth_verifier = flask.request.args.get("oauth_verifier")
    if oauth_token and oauth_verifier:
        consumer = oauth.OAuthConsumer(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
        token = oauth.OAuthToken(oauth_token, None)
        token.set_verifier(oauth_verifier)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token, verifier=oauth_verifier,
            http_method="POST", http_url="https://api.twitter.com/oauth/access_token")
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
        url = oauth_request.to_url()
        try:
            resp = urlfetch.fetch(url).content
        except urlfetch.Error:
            resp = ""
        access_token = dict(urlparse.parse_qsl(resp))
        oauth_token = access_token.get("oauth_token")
        oauth_token_secret = access_token.get("oauth_token_secret")
        if oauth_token and oauth_token_secret:
            flask.session["oauth_token"] = oauth_token
            flask.session["oauth_token_secret"] = oauth_token_secret
            return flask.redirect(flask.url_for("home_timeline"))
    return flask.redirect(flask.url_for("login"))


