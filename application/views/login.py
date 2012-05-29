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


@app.route("/oauth/", methods=["POST"])
def oauth_login():
    app_password = app.config["INVITE_CODE"]
    if (app_password and app_password == flask.request.form.get("invitecode")) or (not app_password):
        consumer = oauth.OAuthConsumer(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"])
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
            callback=flask.url_for("oauth_callback"),
            http_url="https://api.twitter.com/oauth/request_token")
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
        url = oauth_request.to_url()
        resp = urlfetch.fetch(url).content
        request_token = dict(urlparse.parse_qsl(resp))
        oauth_token = request_token['oauth_token']
        return flask.redirect("https://api.twitter.com/oauth/authorize?oauth_token=%s" % oauth_token)
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback/")
def oauth_callback():
    pass

