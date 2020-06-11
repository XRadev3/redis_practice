import datetime
import flask
import logging

from app import auth_utils
from redis_utils import redis_utils
from functools import wraps


def require_auth(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        try:
            expiration_key = auth_utils.cache.key_prefix + flask.session['username']

            if redis_utils.key_exists(expiration_key):

                if not rate_limiter():
                    response = flask.make_response(flask.redirect(f'/', ), 401, )
                    return response

                return view_function(*args, **kwargs)

            else:
                flask.session.pop('username', None)
                return flask.redirect(flask.request.url)

        except Exception as message:
            logging.log(logging.INFO, str(message))
            response = flask.make_response(flask.redirect(f'/', ), 401, )
            return response

    return decorated_function


def require_apikey(view_function):
    @wraps(view_function)
    def decorator(*args, **kwargs):
        try:
            if auth_utils.check_api_key_exists(flask.request.headers['API_KEY']):
                if not rate_limiter(agent=True):
                    return view_function(*args, **kwargs)

                else:
                    return {"data": "You have made too much requests!", "status": 401}

        except Exception as message:
            return flask.abort(401)

        return flask.abort(401)

    return decorator


def rate_limiter(agent=False):
    if not agent:
        username = flask.session['username']
        api_key = auth_utils.get_api_key(username)
    else:
        api_key = flask.request.headers['API_KEY']
        item_data = auth_utils.get_json_from_file('', api_key)
        username = list(item_data.keys())[0]

    try:
        now = datetime.datetime.now()
        redis_key_per_minute = api_key + "-" + str(now.minute)
        redis_key_hourly = api_key + "-" + str(now.hour) + "-hour"
        user_group_limits = auth_utils.get_group_info(redis_utils.hget(username, auth_utils.cache.item_hash_field))

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
    #
    # finally:
    #     import pdb;pdb.set_trace()
    #     print('hi')