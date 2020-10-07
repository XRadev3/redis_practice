# This file contains all the redis functionality.
# Most of the functions are self explanatory and do not contain comments for instructions.

import redis
import logging

r_cli = redis.Redis("172.17.0.2", "6379")


###### HASH ######


def hset(hash_name, hash_map):
    """
    Redis hset command:
    hash_name -> key(string)
    hash_map -> dict, can be nested.
    If successful returns True, otherwise False
    """

    try:
        r_hash = r_cli.hset(name=hash_name, mapping={'attributes': str(hash_map)})
        if r_hash:
            return True

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def hdel(hash_name, hash_key):
    """
    Redis hdel command:
    hash_name -> key(string)
    hash_key -> key(string)
    If successful returns True, otherwise False.
    """

    try:
        r_hash = r_cli.hdel(hash_name, hash_key)
        if r_hash:
            return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def hget(hash_name, hash_key):
    """
    Redis hget command:
    hash_name -> Redis key(string)
    hash_key -> Redis field(string)
    If successful returns dict object, otherwise False.
    """
    try:
        r_hash = r_cli.hget(name=hash_name, key=hash_key)
        if r_hash:
            return eval(r_hash.decode())

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def hget_from_all(key):
    """
    Redis hget command:
    hash_name -> Redis key(string)
    If successful returns dict object, otherwise False.
    """

    all_hashes = decode_bytelist(r_cli.scan(0)[1])
    try:
        for hash_name in all_hashes:
            request_data = hget(hash_name, key)

            if request_data['status'] == 201:
                return request_data

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def hlen(key):
    """
    Redis hlen command:
    key -> Redis key(string)
    If successful returns integer,
    otherwise returns False.
    """
    try:
        # DOES NOT RETURN SIZE BUT NUMBER OF ITEMS INSIDE THE HASH!!!!!! I NEED TO CHANGE IT.
        size = r_cli.hlen(key)
        return int(size)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


###### SETS ######


def get_ordered_set_details(set_name, member=str()):
    """
    Redis zcard and zscore commands:
    set_name -> Redis key(string)
    member -> Redis member(string)
    If successful returns the length of the ordered_set,
    and if member given, returns the score of the member,
    otherwise False.
    """

    try:
        if not member:
            size = r_cli.zcard(set_name)
            return size

        else:
            score = r_cli.zscore(set_name, member)
            return score

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zincrby_to_highest(set_name, member, decrement_higher=False):
    """
    Redis zincrby command:
    set_name -> Redis key(string)
    member -> Redis member(string)
    Set the score of member to higest + 1.
    If successful returns True and if decrement_higher is True,
    decrement the higher from input value members,
    otherwise return False.
    """

    try:
        all_items = zrange_by_score(set_name)
        if member not in all_items:
            return False

        item_index = all_items.index(member)
        key_score = zscore(set_name, member)
        score_to_incr = len(all_items) - key_score

        if decrement_higher:
            for i in range(item_index + 1, len(all_items)):
                r_cli.zincrby(set_name, -1, all_items[i])

        r_cli.zincrby(set_name, score_to_incr, member)
        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zrange_by_score(set_name):
    """
    Redis zrangebyscore command:
    set_name -> Redis key(string)
    If successful returns dict object,
    otherwise returns False.
    """
    try:
        size = get_ordered_set_details(set_name)
        all_items_by_score = r_cli.zrangebyscore(set_name, 0, size)
        return decode_bytelist(all_items_by_score)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def hgetall(hash_name):
    """
    Redis hgetall command:
    hash_name -> Redis key(string)
    If successful returns dict object,
    otherwise returns False.
    """

    try:
        all_users = r_cli.hgetall(name=hash_name)
        r_hash = decode_bytelist(all_users, nested_to_dict=True)

        if all_users:
            return r_hash

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zscore(set_name, key):
    """
    Redis zscore command:
    set_name -> Redis key(string)
    member -> Redis member(string)
    If successful returns float,
    otherwise return False.
    """

    try:
        return r_cli.zscore(set_name, key)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zrange(set_name, start=0, end=-1):
    """
    Redis zrange start end command:
    set_name -> Redis key(string)
    start -> Integer
    end -> Integer
    If successful returns list,
    otherwise returns False.
    """

    try:
        output = r_cli.zrange(set_name, start, end)
        return decode_bytelist(output)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zrange_lowest_score(set_name, all_items=False):
    """
    Redis zrange and zscore commands:
    set_name -> Redis key(string)
    If successful returns the member's key with the lowest score,
    if all_items is True, returns a list of all items from the os, sorted by score.
    otherwise returns False.
    """

    try:
        if not all_items:
            all_items = r_cli.zrange(set_name, 0, -1)
            all_items_sorted = r_cli.zrangebyscore(set_name, 0, len(all_items))
            lowest_score_name = all_items_sorted[0].decode()

            return lowest_score_name

        return decode_bytelist(all_items)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zadd(set_name, member, score):
    """
    Redis add command:
    set_name -> Redis key(string)
    member -> Redis member(string)
    score -> Redis score(int)
    If successful returns True,
    otherwise returns False.
    """
    try:
        if r_cli.zadd(set_name, {member: score}):
            return True

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zrem(set_name, member):
    """
    Redis zrem command:
    set_name -> Redis key(string)
    member -> Redis member(string)
    If successful returns True,
    otherwise returns False.
    """
    try:
        if r_cli.zrem(set_name, member):
            return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def zrange_singular(set_name, member):
    """
    Redis zrange command:
    set_name -> Redis key(string)
    member -> Redis member(string)
    If successful returns True,
    otherwise returns False.
    """
    try:
        member_dict = [x.decode() for x in r_cli.zrange(set_name, 0, -1)]
        if member in member_dict:
            return True

        return False

    except ValueError as message:
        return False


###### KEYS ######


def set_key(name, value, expiration_time=int()):
    """
    Redis set command:
    name -> Redis key(string)
    value -> string value.
    expiration_time -> key expiration time(int)
    If successful returns True,
    otherwise returns False.
    """
    try:
        if expiration_time:
            r_cli.set(name=name, value=value, ex=expiration_time)
            return True
        else:
            r_cli.set(name=name, value=value)
            return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def get_key(key):
    """
    Redis get command:
    name -> Redis key(string)
    If successful returns string,
    otherwise returns False.
    """
    try:
        key_value = r_cli.get(key)

        if key_value:
            return key_value.decode()

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def incr_key(key, by=int()):
    """
    Redis incr command:
    key -> Redis key(string)
    by -> amount(integer)
    Increments the key by one,
    if by is given, increments by the given number,
    If successful returns the new value, otherwise returns False.
    """

    try:
        if by:
            return r_cli.incr(key, by)

        return r_cli.incr(key)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def key_exists(key):
    """
    Redis keys command:
    key -> Redis key(string)
    If key exists returns True,
    otherwise returns False.
    """

    try:
        key_name = r_cli.keys(key)
        if key_name:
            return True

        return False

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def set_expiration(key, expiration_time):
    """
    Redis expire command:
    key -> Redis key(string)
    expiration_time -> key expiration time(integer)
    If successful returns True,
    otherwise returns False.
    """

    try:
        r_cli.expire(key, expiration_time)
        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def get_expiration_time(key):
    """
    Redis ttl command:
    key -> Redis key(string)
    If successful returns the expiration time of the key,
    otherwise returns False
    """

    try:
        return r_cli.ttl(key)

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def make_persistent(key):
    """
    Redis persist command:
    key -> Redis key(string)
    If successful returns True,
    otherwise return False.
    """

    try:
        r_cli.persist(key)
        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def rem_key(key):
    """
    Redis del command:
    key -> Redis key(string)
    If successful returns True,
    otherwise return False
    """

    try:
        r_cli.delete(key)
        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


###### OTHER ######


def get_redis_info(single_value=False):
    """
    Redis info command.
    Returns dict, if single_value is True, returns string,
    otherwise returns False.
    """
    try:
        all_info = r_cli.info()

        if single_value:

            info = all_info[single_value]
            return info

        return all_info

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def flushall():
    """
    Redis flushall command:
    *static
    NOTE! NO GOING BACK.. everything will be gone.
    """

    r_cli.flushall()


def decode_bytelist(bytelist, nested_to_dict=False):
    """
    bytelist -> list(bytes)
    If successful returns list,
    otherwise returns False.
    """

    if nested_to_dict:
        result = dict()

        for x in bytelist:
            result.update({x.decode(): bytelist[x]})

    else:
        result = [x.decode() for x in bytelist]

    return result
