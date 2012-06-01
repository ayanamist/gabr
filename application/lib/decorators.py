import functools

import flask

def login_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if not flask.g.api:
            return flask.redirect(flask.url_for("login"))
        return func(*args, **kwargs)

    return decorated_view


def templated(template=None):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = flask.request.endpoint.replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return flask.render_template(template_name, **ctx)

        return decorated_function

    return decorator