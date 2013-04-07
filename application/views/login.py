from __future__ import absolute_import

import flask
import twython

from application import app
from application.utils import abs_url_for
from application.utils import decorators


@app.route("/login")
@decorators.templated()
def login():
    return {
        "title": "Login",
    }


@app.route("/oauth")
def oauth_login():
    flask.g.api.callback_url = abs_url_for("oauth_callback")
    flask.g.api.authenticate_url = flask.g.api.authorize_url
    try:
        redirect_url = flask.g.api.get_authentication_tokens()['auth_url']
        return flask.redirect(redirect_url)
    except twython.TwythonError, e:
        flask.flash("OAuth error:%s, please try again." % str(e))
        return flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback")
def oauth_callback():
    flask.g.api = twython.Twython(app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRET"],
        flask.request.args.get("oauth_token"), flask.request.args.get("oauth_verifier"))
    try:
        flask.session.update(flask.g.api.get_authorized_tokens())
    except twython.Twython, e:
        flask.flash("OAuth error:%s, please try again." % str(e))
        return flask.redirect(flask.url_for("login"))
    else:
        last_url = flask.session.get("last_url")
        if last_url:
            flask.session["last_url"] = ""
            return flask.redirect(last_url)
        else:
            return flask.redirect(flask.url_for("home_timeline"))


@app.route("/logout")
def logout():
    del flask.session["screen_name"]
    del flask.session["oauth_token"]
    del flask.session["oauth_token_secret"]
    flask.flash("Logout successfully!")
    return flask.redirect(flask.url_for("login"))