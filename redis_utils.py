import redis

r_cli = redis.StrictRedis()


def hset(hash_name, hash_key, hash_value, multiple=False):
    msg = 'Input data is incorrect!'
    method_to_use = r_cli.hset

    if multiple:
        # Do not use yet
        # hash_value input type should be a dict first.
        method_to_use = r_cli.hmset

    try:
        r_hash = method_to_use(name=hash_name, key=hash_key, value=hash_value)
        if r_hash:
            return {'data': True, 'status': 201}

        elif r_hash == 0:
            return {'data': msg, 'status': 400}

        return {'data': msg, 'status': 400}

    except Exception as msg:
        return {'data': msg, 'status': 500}


def hdel(hash_name, hash_key):
    msg = 'Input data is incorrect!'

    try:
        r_hash = r_cli.hdel(hash_name, hash_key)
        if r_hash:
            return {'data': True, 'status': 204}

        elif r_hash == 0:
            return {'data': msg, 'status': 400}

        return {'data': msg, 'status': 400}

    except Exception as msg:
        return {'data': msg, 'status': 500}


def hget(hash_name, hash_key):
    msg = 'Input data is incorrect!'

    try:
        r_hash = r_cli.hget(name=hash_name, key=hash_key)
        if r_hash:
            return {'data': r_hash.decode(), 'status': 201}

        elif r_hash == 0:
            return {'data': msg, 'status': 400}

        return {'data': msg, 'status': 400}

    except Exception as msg:
        return {'data': msg, 'status': 500}


def hgetall(hash_name):
    msg = 'Input data is incorrect!'
    r_hash = dict()

    try:
        all_users = r_cli.hgetall(name=hash_name)
        for x in all_users:
            r_hash.update({x.decode(): all_users[x].decode()})

        if all_users:
            return {'data': r_hash, 'status': 201}

        elif r_hash == 0:
            return {'data': msg, 'status': 400}

        return {'data': msg, 'status': 400}

    except Exception as msg:
        return {'data': msg, 'status': 500}


def zrange(request_data):
    return r_cli.zrange(request_data["base"], 0, -1)


def zadd(request_data):
    try:
        user_status = r_cli.zadd(request_data["base"], {request_data["value"]: request_data["score"]})
        return user_status

    except Exception as msg:
        return False


def zrem(request_data):
    try:
        user_status = r_cli.zrem(request_data["base"], request_data["value"])
        return user_status

    except Exception as msg:
        return False


def zrange_singular(sorted_set, key):
    try:
        key_dict = [x.decode() for x in r_cli.zrange(sorted_set, 0, -1)]
        if key in key_dict:
            return {"data": key, "status": 200}

        raise ValueError('The given key does not exist in the given ordered set')

    except ValueError as msg:
        return {"data": str(msg), "status": 400}


def flushall():
    r_cli.flushall()