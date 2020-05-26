# This file contains all the redis functionality.
# Most of the functions are self explanatory and do not contain comments for instructions.

import redis
import json
import os

r_cli = redis.StrictRedis()
admin_file = os.getcwd() + '/local_storage/administrators.txt'
users_file = os.getcwd() + '/local_storage/users.txt'


###### HASH ######


def hset(hash_name, hash_map):
    msg = 'Input data is incorrect!'

    try:
        r_hash = r_cli.hset(name=hash_name, mapping={'attributes': str(hash_map)})
        if r_hash:
            json_to_file({hash_name: {'attributes': hash_map}})
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
        r_hash = decode_bytelist(all_users, nested_to_dict=True)

        if all_users:
            return {'data': r_hash, 'status': 201}

        elif r_hash == 0:
            return {'data': msg, 'status': 400}

        return {'data': msg, 'status': 400}

    except Exception as msg:
        return {'data': msg, 'status': 500}


def hget_from_all(key):
    all_hashes = decode_bytelist(r_cli.scan(0)[1])
    try:
        for hash_name in all_hashes:
            request_data = hget(hash_name, key)

            if request_data['status'] == 201:
                return request_data

    except Exception as message:
        return {'data': message, 'status': 400}

###### SETS ######


def zrange(set_name):
    return r_cli.zrange(set_name, 0, -1)


def zadd(set_name, key, score):
    try:
        user_status = r_cli.zadd(set_name, {key: score})
        return user_status

    except Exception as msg:
        return False


def zrem(set_name, key):
    try:
        user_status = r_cli.zrem(set_name, key)
        return user_status

    except Exception as msg:
        return False


def zrange_singular(set_name, key):
    try:
        key_dict = [x.decode() for x in r_cli.zrange(set_name, 0, -1)]
        if key in key_dict:
            return {"data": key, "status": 200}

        raise ValueError('The given key does not exist in the given ordered set')

    except ValueError as msg:
        return {"data": str(msg), "status": 400}

###### KEYS ######


def set_key(name, value, expiration_time=None):
    try:
        if expiration_time:
            r_cli.set(name=name, value=value, ex=expiration_time)
            return True
        else:
            r_cli.set(name=name, value=value)
            return True

    except Exception as message:
        return False


def get_key(name):
    try:
        r_cli.get(name)
        return True

    except Exception as message:
        return False


def set_expiration(name, expiration_time):
    try:
        r_cli.expire(name, expiration_time)
        return True

    except Exception as message:
        return False


def get_expiration_time(name):
    try:
        return r_cli.ttl(name)

    except Exception as message:
        return False


def make_persistent(name):
    try:
        r_cli.persist(name)
        return True

    except Exception as message:
        return False


def rem_key(name):
    try:
        r_cli.delete(name)
        return True

    except Exception as message:
        return False

###### OTHER ######


# Writes a given json data to a file. If unsuccessful the function will return false, otherwise true.
def json_to_file(json_data, admin=False):
    if admin:
        path_to_use = admin_file
    else:
        path_to_use = users_file

    try:
        with open(path_to_use, 'a') as output_file:
            output_file.write("\n")
            json.dump(json_data, output_file)
            return True

    except Exception as message:
        return False


# Reads a given json file to a json object.
# If to_hash is set to true, the function will return a json data ready to be parsed to a Redis hash.
# If unsuccessful the function will return false, otherwise the requested object.
def json_file_to_hash(hash_name, to_hash=False):
    files = [users_file, admin_file]

    for path_to_use in files:
        try:
            with open(path_to_use, 'r') as input_file:

                for line in input_file:
                    if line == "\n":
                        pass
                    elif hash_name in line:
                        json_data = json.loads(line)
                        return json_data

        except Exception as message:
            return False

    return False


# Use to flush all te redis content. WARNING! There is no data restoration after using this function.
def flushall():
    r_cli.flushall()


# Use to decode a list or dict of bytes.
# If nested_to_dict bool is set the function will return a dictionary from a nested list.
def decode_bytelist(bytelist, nested_to_dict=False):
    if nested_to_dict:
        result = dict()

        for x in bytelist:
            result.update({x.decode(): bytelist[x].decode()})

    else:
        result = [x.decode() for x in bytelist]

    return result
