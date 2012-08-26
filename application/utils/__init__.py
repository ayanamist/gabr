import flask

from application import app

abs_url_for = lambda endpoint, **values: flask.request.host_url + flask.url_for(endpoint, **values)
app.jinja_env.globals.update(
    abs_url_for=abs_url_for
)

def parse_params():
    params = dict()
    for access_param in ("max_id", "page", "since_id", "count"):
        param = flask.request.args.get(access_param)
        if param:
            try:
                param = int(param, 10)
                params[access_param] = param
            except ValueError:
                pass
    return params


def remove_max_id(iterable, max_id):
    if max_id:
        for i, result in enumerate(iterable):
            if result.get("id_str") == max_id or result.get("max_position") == max_id:
                del iterable[i]
    return iterable

