import flask
import redis_utils

from functools import wraps


def require_auth():
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            user = flask.request.headers['User']
            ordered_set = flask.request.args.to_dict()

            if redis_utils.get_key_from_ordered_set(ordered_set['base'], user):
                return view_function(*args, **kwargs)

            else:
                flask.abort(401)

        return decorated_function

    return decorator

