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


def get_key_from_ordered_set(request_data):
    try:
        users = r_cli.zrange(request_data["base"], 0, -1)
        import pdb;pdb.set_trace()
        if request_data['value'] in users:
            return users[request_data['value']]

    except Exception as msg:
        return False


def clear_redis():
    r_cli.flushall()
