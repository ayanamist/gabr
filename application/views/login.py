from __future__ import absolute_import

import flask

from application import app
from application.models import twitter
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
    flask.g.api.bind_auth()
    try:
        request_tokens = flask.g.api.get_authentication_tokens(callback_url=abs_url_for("oauth_callback"))
        if request_tokens["oauth_callback_confirmed"] != "true":
            raise twitter.Error("OAuth callback not confirmed")
    except twitter.Error as e:
        flask.flash("OAuth error: %s, please try again." % str(e))
        return flask.redirect(flask.url_for("login"))
    else:
        return flask.redirect(request_tokens["auth_url"])


@app.route("/oauth_callback")
def oauth_callback():
    oauth_token = flask.request.args.get("oauth_token")
    oauth_verifier = flask.request.args.get("oauth_verifier")
    try:
        if oauth_token and oauth_verifier:
            flask.g.api.bind_auth(oauth_token, oauth_verifier=oauth_verifier)
            flask.session.update(flask.g.api.get_authorized_tokens())
        else:
            raise twitter.Error("OAuth callback does not have necessary parameters")
    except twitter.Error as e:
        flask.flash("OAuth error: %s, please try again." % str(e))
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