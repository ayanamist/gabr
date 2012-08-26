import flask
import twython

from ..utils import decorators
from ..utils import abs_url_for
from application import app

@app.route("/login")
@decorators.templated()
def login():
    return {
        "title": "Login",
        }


@app.route("/oauth")
def oauth_login():
    flask.g.api.callback_url = "%s%s" % (flask.request.host_url, abs_url_for("oauth_callback"))
    flask.g.api.authenticate_url = flask.g.api.authorize_url
    try:
        redirect_url = flask.g.api.get_authentication_tokens()['auth_url']
        return flask.redirect(redirect_url)
    except twython.TwythonError, e:
        flask.flash("OAuth error:%s, please try again." % str(e))
        return flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback")
def oauth_callback():
    flask.session.permanent = True
    flask.g.api.oauth_token = flask.request.args.get("oauth_token")
    flask.g.api.oauth_token_secret = flask.request.args.get("oauth_verifier")
    try:
        flask.session.update(flask.g.api.get_authorized_tokens())
        return flask.redirect(flask.url_for("home_timeline"))
    except twython.Twython, e:
        flask.flash("OAuth error:%s, please try again." % str(e))
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