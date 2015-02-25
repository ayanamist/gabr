from __future__ import absolute_import

import flask

from application import utils
from application.models import twitter
from application.utils import decorators


@decorators.templated()
def login():
    tpl_data = {
        "title": "Login",
    }
    if flask.request.method == "POST":
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        if username and password:
            flask.g.api.bind_auth()
            params = {
                "x_auth_mode": "client_auth",
                "x_auth_username": username,
                "x_auth_password": password,
            }
            try:
                flask.session.update(flask.g.api.get_authorized_tokens(**params))
            except twitter.Error as e:
                flask.flash("XAuth error: %s, please try again." % str(e))
            else:
                last_url = flask.session.get("last_url")
                if last_url:
                    flask.session["last_url"] = ""
                    return flask.redirect(last_url)
                else:
                    return flask.redirect(utils.abs_url_for("home_timeline"))
        else:
            flask.flash("Username & Password are both required!")
    return tpl_data


def logout():
    del flask.session["screen_name"]
    del flask.session["oauth_token"]
    del flask.session["oauth_token_secret"]
    flask.flash("Logout successfully!")
    return flask.redirect(utils.abs_url_for("login"))