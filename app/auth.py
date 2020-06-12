import datetime
import flask
import logging

from app import auth_utils
from functools import wraps
from redis_utils import redis_utils
from werkzeug import exceptions as w_exceptions


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
                flask.session['username'] = auth_utils.check_api_key_exists(flask.request.headers['API_KEY'], True)

                if not rate_limiter():
                    return {"data": "You have made too much requests!", "status": 401}

                else:
                    return view_function(*args, **kwargs)

        except Exception as message:
            return flask.abort(401)

        return flask.abort(401)

    return decorator


def increment_limiter(response):
    try:
        api_key = response.headers['API_KEY']

    except w_exceptions.BadRequestKeyError:
        username = flask.session['username']
        api_key = auth_utils.get_api_key(username)

    except KeyError:
        return response

    try:
        now = datetime.datetime.now()
        number_limit_key_per_minute = api_key + "-" + str(now.minute)
        number_limit_key_hourly = api_key + "-" + str(now.hour) + "-hour"
        traffic_key_hourly = api_key + "-" + str(now.hour) + "-hourly_traffic"
        data_size = response.headers['data_size']

        # Increment the number of requests made by the user.
        redis_utils.incr_key(number_limit_key_per_minute)
        redis_utils.incr_key(number_limit_key_hourly)
        redis_utils.set_expiration(number_limit_key_per_minute, 59)
        redis_utils.set_expiration(number_limit_key_hourly, 59 * 60)

        # Add the sent data size to the user traffic.
        redis_utils.incr_key(traffic_key_hourly, by=data_size)
        redis_utils.set_expiration(traffic_key_hourly, 59 * 60)
        logging.log(10, 'Incremented')

    except w_exceptions.BadRequestKeyError:
        pass

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        flask.abort(401)


def rate_limiter():
    try:
        api_key = flask.request.headers['API_KEY']
        username = auth_utils.check_api_key_exists(api_key, True)

    except Exception as message:
        username = flask.session['username']
        api_key = auth_utils.get_api_key(username)

    try:
        now = datetime.datetime.now()
        redis_key_per_minute = api_key + "-" + str(now.minute)
        redis_key_hourly = api_key + "-" + str(now.hour) + "-hour"
        traffic_key_per_hourly = api_key + "-" + str(now.hour) + "-hourly_traffic"

        user_group_limits = auth_utils.get_group_info(auth_utils.get_json_from_file(username)[username][auth_utils.cache.item_hash_field])

        n_rq_per_minute = redis_utils.get_key(redis_key_per_minute)
        n_rq_hourly = redis_utils.get_key(redis_key_hourly)
        user_traffic_hourly = redis_utils.get_key(traffic_key_per_hourly)

        logging.log(10, 'Checked')

        if int(user_traffic_hourly) > user_group_limits['traffic'] and user_traffic_hourly:
            flask.flash('You have reached the data limit. Please wait an hour before making any more. OR buy our premium membership, just pay in the next hour and you will recieve 20% discount!!!')
            return False

        elif int(n_rq_hourly) > user_group_limits['requests']*10 and n_rq_hourly:
            flask.flash('You have reached the maximum allowed requests per hour. Please wait an hour before making any more. OR buy our premium membership, just pay in the next hour and you will recieve 20% discount!!!')
            return False

        elif int(n_rq_per_minute) > user_group_limits['requests'] and n_rq_per_minute:
            flask.flash('You have reached the maximum allowed requests per minute. Please wait a minute before making any more. OR buy our premium membership, just pay in the next hour and you will recieve 20% discount!!!')
            return False

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False
