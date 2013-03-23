import inspect
import logging

from . import render
from . import do_item
from . import do_rfc822
from . import abs_url_for


def patch_logging():
    def logger_debug(*args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_globals["__package__"]
        logger = logging.getLogger(caller_name)
        logger.debug(*args, **kwargs)

    # Replace all direct function callings to logger methods.
    logging.debug = logger_debug

    # Mute noisy logging.
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
    app.jinja_env.filters['rfc822'] = do_rfc822


def patch_all(app=None):
    patch_logging()
    if app:
        patch_jinja2(app)

