import functools

import flask

def login_required(func):
    def is_authenticated():
        try:
            return flask.session.get("oauth_token") and flask.session.get("oauth_token_secret")
        except Exception:
            return False

    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not is_authenticated():
            return flask.redirect(flask.url_for("login"))
        return func(*args, **kwargs)

    return decorated_view