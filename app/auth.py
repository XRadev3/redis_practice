import flask
from redis_utils import redis_utils
from flask import session
from functools import wraps


def require_auth():
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            try:
                if redis_utils.hgetall(session['username']):
                    return view_function(*args, **kwargs)

                else:
                    flask.abort(401)

            except Exception as message:
                flask.abort(401)

        return decorated_function

    return decorator
