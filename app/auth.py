import app.app_utils as app_utils
import datetime

from redis_utils import redis_utils
from flask import session, abort, flash
from functools import wraps


def require_auth():
    def decorator(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            try:
                from app.app import cache
                username = session['username']
                expiration_key = cache.key_prefix + username

                if not rate_limiter(username):
                    flash('Too much requests!')

                if redis_utils.get_key(expiration_key):
                    return view_function(*args, **kwargs)

                else:

                    if session['username']:
                        session.pop('username', None)
                        abort(401)

            except Exception as message:
                abort(401)

        return decorated_function

    return decorator


def check_credentials(username=str, password=str):
    try:
        from app.app import cache
        user_data = app_utils.get_json_from_file(username)
        user_pass = user_data[username][cache.item_hash_field]['password']
        api_key = user_data[username][cache.item_hash_field]['API_KEY']

    except Exception as message:
        return False

    if user_pass == password:
        return True

    else:
        return False


def rate_limiter(username):
    """
    This decorator is used to limit traffic data.

    """
    try:
        now = datetime.datetime.now()
        api_key = app_utils.get_api_key(username)
        redis_key = api_key + "-" + str(now.minute)
        num_requests = int(redis_utils.get_key(redis_key)) if redis_utils.get_key(redis_key) else 0

        if num_requests > 10:
            return False

        redis_utils.incr_key(redis_key)
        redis_utils.set_expiration(redis_key, 59)
        return True

    except Exception as message:
        return message
