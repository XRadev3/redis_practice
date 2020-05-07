import flask

from functools import wraps


def require_appkey():
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            requested_method = flask.request.method

            if ((requested_method not in normal_methods) and
                    (requested_method not in master_methods)):
                return view_function(*args, **kwargs)

            else:
                pass

            machine_key = flask.request.headers['API_KEY']

            if requested_method in master_methods:
                if validate_key(machine_key) == "master":
                    return view_function(*args, **kwargs)

                else:
                    flask.abort(401)

            elif requested_method in normal_methods:
                if validate_key(machine_key) == "normal":
                    return view_function(*args, **kwargs)

                else:
                    flask.abort(401)

            else:
                return view_function(*args, **kwargs)

        return decorated_function

    return decorator
