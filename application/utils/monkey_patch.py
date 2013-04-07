import inspect
import logging

import twython

from . import do_item
from . import do_rfc822
from . import abs_url_for
from application.libs import render


def patch_logging():
    def logger_wrap(func):
        def logger_log(*args, **kwargs):
            caller_frame = inspect.currentframe().f_back
            caller_name = caller_frame.f_globals["__package__"]
            logger = logging.getLogger(caller_name)
            getattr(logger, func.__name__)(*args, **kwargs)

        return logger_log

    # Replace all direct function callings to logger methods.
    for func_name in ("critical", "error", "exception", "warn", "warning", "info", "debug", "log"):
        setattr(logging, func_name, logger_wrap(getattr(logging, func_name)))

    # Mute noisy logging.
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("oauthlib").setLevel(logging.ERROR)


def patch_jinja2(app):
    app.jinja_env.globals.update(
        abs_url_for=abs_url_for,
        prerender_tweet=render.prerender_tweet,
        render_created_at=render.render_created_at,
    )
    app.jinja_env.filters['item'] = do_item
    app.jinja_env.filters['rfc822'] = do_rfc822


def patch_twython():
    def str_exception(self):
        return "%s %s" % (
            self.error_code, twython.twitter_endpoints.twitter_http_status_codes.get(self.error_code, ["Unknown"])[0])

    twython.TwythonError.__str__ = str_exception


def patch_all(app=None):
    patch_logging()
    patch_twython()
    if app:
        patch_jinja2(app)

