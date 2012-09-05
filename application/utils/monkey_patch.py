import logging

import requests

from .import render
from .import do_item
from .import abs_url_for

def patch_logging():
    # Mute noisy logging.
    # Use my own mod oauthlib instead of original one, because the original author is not friendly with developers.
    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("oauthlib").setLevel(logging.CRITICAL)


def patch_jinja2(app):
    app.jinja_env.globals.update(
        abs_url_for=abs_url_for
    )
    app.jinja_env.globals.update(
        prerender_tweet=render.prerender_tweet,
        render_created_at=render.render_created_at,
    )
    app.jinja_env.filters['item'] = do_item

# Patch requests not to verify SSL, it's unnecessary for GAE.
def _requests_wrap(f):
    def wrapped(**kwargs):
        kwargs["verify"] = False
        return f(**kwargs)

    return wrapped


def patch_requests():
    requests.session = _requests_wrap(requests.session)


def patch_all(app=None):
    patch_logging()
    patch_requests()
    if app:
        patch_jinja2(app)

