from __future__ import absolute_import

import flask

from application import utils
from application.utils import decorators


@decorators.templated()
def login():
    tpl_data = {
        "title": "Login",
    }
    if flask.request.method == "POST":
        oauth_token = flask.request.form.get("oauth_token")
        if not oauth_token:
            try:
                flask.g.api.bind_auth()
                token_data = flask.g.api.get_authentication_tokens(callback_url="oob")
                tpl_data["auth_url"] = token_data["auth_url"]
                tpl_data["oauth_token"] = token_data["oauth_token"]
            except Exception as e:
                flask.flash("OAuth get authentication tokens error: %s, please try again." % str(e))
        else:
            oauth_verifier = flask.request.form.get("oauth_verifier")
            if not oauth_verifier:
                tpl_data.update(flask.request.form)
                flask.flash("Pin is required!")
            else:
                flask.g.api.bind_auth(oauth_token=oauth_token, oauth_verifier=oauth_verifier)
                try:
                    flask.session.update(
                        flask.g.api.get_authorized_tokens(oauth_token=oauth_token, oauth_verifier=oauth_verifier))
                except Exception as e:
                    flask.flash("OAuth get access token error: %s, please try again." % str(e))
                else:
                    last_url = flask.session.get("last_url")
                    if last_url:
                        flask.session["last_url"] = ""
                        return flask.redirect(last_url)
                    else:
                        return flask.redirect(utils.abs_url_for("home_timeline"))
    return tpl_data


def logout():
    del flask.session["screen_name"]
    del flask.session["oauth_token"]
    del flask.session["oauth_token_secret"]
    flask.flash("Logout successfully!")
    return flask.redirect(utils.abs_url_for("login"))
