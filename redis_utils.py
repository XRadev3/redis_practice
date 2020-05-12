import redis

from rq import Queue

r_cli = redis.StrictRedis()
#queue = Queue(connection=r_cli.connection())


def display_zsets(request_data):
    return r_cli.zrange(request_data["base"], 0, -1)


def add_ordered_set(request_data):
    try:
        user_status = r_cli.zadd(request_data["base"], {request_data["value"]: request_data["score"]})
        return user_status

    except Exception as msg:
        return False


def remove_ordered_set(request_data):
    try:
        user_status = r_cli.zrem(request_data["base"], request_data["value"])
        return user_status

    except Exception as msg:
        return False


def get_key_from_ordered_set(sorted_set, key):
    try:
        key_dict = [x.decode() for x in r_cli.zrange(sorted_set, 0, -1)]
        if key in key_dict:
            return {"data": key, "status": "200"}

        raise ValueError('The given key does not exist in the given ordered set')

    except Exception as msg:
        return {"data": str(msg), "status": 400}


def clear_redis():
    r_cli.flushall()
