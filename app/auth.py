import app.auth_utils as app_utils
import datetime

from redis_utils import redis_utils
from flask import session, abort, flash
from functools import wraps


def require_auth():
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            try:
                username = '*' + session['username']

                if redis_utils.get_key_name(username):
                    return view_function(*args, **kwargs)

                else:
                    if session['username']:
                        session.pop('username', None)
                        abort(401)

            except Exception as message:
                abort(401)

        return decorated_function

    return decorator


def check_password(username, password):
    user_data = app_utils.get_json_from_file(username)
    user_pass = user_data[username]['attributes']['password']

    if app_utils.check_key(user_pass, password):
        return True


def check_api_key(username, api_key):
    try:
        from app.app import cache
        user_data = app_utils.get_json_from_file(username)
        user_api_key = user_data[username][cache.item_hash_field]['API_KEY']

    except Exception as message:
        return False


def rate_limiter():
    """
    This decorator is used to limit traffic data.

    """
    try:
        from app.app import cache

        username = session['username']
        now = datetime.datetime.now()
        api_key = app_utils.get_api_key(username)
        redis_key_hourly = api_key + "-" + str(now.minute)
        user_group_limits = app_utils.get_group_info(redis_utils.hget(username, cache.item_hash_field))

        n_rq_hourly = redis_utils.incr_key(redis_key_hourly)
        redis_utils.set_expiration(redis_key_hourly, 59)

        import pdb;pdb.set_trace()
        if n_rq_hourly > user_group_limits['requests']:
            flash('You have reached the maximum allowed requests. Please wait an hour before making any more.')

        return True

    except Exception as message:

        return False
