import app.auth_utils as app_utils
import datetime
import flask
import logging

from app.config import cache
from redis_utils import redis_utils
from functools import wraps


def require_auth(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        try:
            username = '*' + flask.session['username']

            if redis_utils.key_exists(username):
                if not rate_limiter():
                    response = flask.make_response(flask.redirect('/', ), 401, )
                    return response

                return view_function(*args, **kwargs)

            else:
                if flask.session['username']:
                    flask.session.pop('username', None)

                    return view_function(*args, **kwargs)

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            response = flask.make_response(flask.redirect('/', ), 401, )
            return response

    return decorated_function


def rate_limiter():
    try:
        username = flask.session['username']
        now = datetime.datetime.now()
        api_key = app_utils.get_api_key(username)
        redis_key_per_minute = api_key + "-" + str(now.minute)
        redis_key_hourly = api_key + "-" + str(now.hour) + "-hour"
        user_group_limits = app_utils.get_group_info(redis_utils.hget(username, cache.item_hash_field))

        redis_utils.incr_key(redis_key_per_minute)
        redis_utils.incr_key(redis_key_hourly)
        redis_utils.set_expiration(redis_key_per_minute, 59)
        redis_utils.set_expiration(redis_key_hourly, 59*60)

        n_rq_per_minute = redis_utils.get_key(redis_key_per_minute)
        n_rq_hourly = redis_utils.get_key(redis_key_hourly)

        if int(n_rq_hourly) > user_group_limits['requests']*10:
            flask.flash('You have reached the maximum allowed requests per hour. Please wait an hour before making any more. OR buy our premium membership, just pay in the next hour and you will recieve 20% discount!!!')
            return False

        elif int(n_rq_per_minute) > user_group_limits['requests']:
            flask.flash('You have reached the maximum allowed requests per minute. Please wait a minute before making any more. OR buy our premium membership, just pay in the next hour and you will recieve 20% discount!!!')
            return False

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def check_password(username, password):
    try:
        user_data = app_utils.get_json_from_file(username)
        user_pass = user_data[username]['attributes']['password']

        if app_utils.check_key(user_pass, password):
            return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        response = flask.make_response(flask.redirect('/', ), 401, )
        return response


# IN PROGRESS
def check_api_key(username, api_key):
    try:
        user_data = app_utils.get_json_from_file(username)
        user_api_key = user_data[username][cache.item_hash_field]['API_KEY']

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False
