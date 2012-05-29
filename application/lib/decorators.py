import functools

import flask

def login_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if False:
            flask.redirect("")
        return func(*args, **kwargs)

    return decorated_view