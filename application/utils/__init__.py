import flask

abs_url_for = lambda endpoint, **values: flask.request.host_url + flask.url_for(endpoint, **values)

def parse_params():
    return flask.request.args.to_dict()


def remove_status_by_id(iterable, max_id):
    if max_id:
        for i, result in enumerate(iterable):
            if result.get("id_str") == max_id or result.get("max_position") == max_id:
                del iterable[i]
    return iterable


def do_item(environment, obj, name):
    try:
        name = str(name)
    except UnicodeError:
        pass
    else:
        try:
            value = obj[name]
        except (TypeError, KeyError):
            pass
        else:
            return value
    return environment.undefined(obj=obj, name=name)
