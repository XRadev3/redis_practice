"""
This file contains all the functionality of the caching system.
The Cache class works with Redis as a data store.
"""
import random
from redis_utils import redis_utils
from functools import wraps
from flask import session, abort


item_hash_field = 'attributes'
key_name = 'key'


class Cache:

    def __init__(self, default_expiration=180, name='cache'):
        """
        default_expiration: the default expiration time of a key in cache in minutes.
        name: the name of the Redis ordered_set used by the cache.
        NOTE: while the cache is empty, this ordered_set is not defined.
        """
        self.name = name
        self.default_expiration = default_expiration

    def get_cache(self):
        """
        This function returns all items currently active in the cache in a list.
        """
        data_store_list = redis_utils.decode_bytelist(redis_utils.zrange(self.name))
        return data_store_list

    def get_key_from_set(self, key):
        """
        This function returns a single key from the cache.
        """
        try:
            cache = redis_utils.decode_bytelist(redis_utils.zrange(self.name))
            for item in cache:
                if key in item:
                    return item

            return False

        except Exception as message:
            return message

    def set_os(self, key_name, score):
        """
        Arguments to create a ordered_set: set name, key name, key value.
        The same way we add a key to a ordered_set.
        """
        try:
            redis_utils.zadd(self.name, key_name, score)
            redis_utils.zrange(self.name)
            return True

        except Exception as message:
            return False

    def set_expiration_key(self, key_value, expiration_time=None):
        """
        This function sets a key with expiration time. The key name is default to "keyN" where N=key_value.
        By default the expiration time will be set to 15 min.
        """
        if expiration_time:
            time_to_set = expiration_time
        else:
            time_to_set = self.default_expiration

        try:
            redis_utils.set_key("key" + session['username'], key_value, time_to_set)
            return True

        except Exception as message:
            return False

    def get_expiration_key(self, key_name, time_only=False):
        """
        This function returns a active key and its expiration time.
        If time_only is set, return the expiration time left on the key as a string.
        Else if it is successful, it will return they key name and expiration time as a list.
        """
        try:
            if time_only:
                return redis_utils.get_expiration_time(key_name)

            else:
                exp_time = redis_utils.get_expiration_time(key_name)
                key = redis_utils.get_key(key_name)
                return [exp_time, key]

        except Exception as message:
            return False

    def make_key_persistent(self, key_name):
        """
        This function makes a key persistent. In other words, removes its expiration time.
        """
        try:
            status = redis_utils.make_persistent(key_name)
            return status

        except Exception as message:
            return False

    def rem_key(self, key_name):
        """
        This function deletes a key and it's instance in the ordered set as well as the hash data.
        """
        try:
            redis_utils.zrem(self.name, key_name)
            redis_utils.rem_key(key_name)
            redis_utils.hdel(key_name, item_hash_field)

            return True

        except Exception as message:
            return False

    def set_hash(self, hash_name):
        """
        This function reads the key data from the storage by its hash_name.
        If successful it will create a Redis hash object that will hold the read data.
        If unsuccessful it will return False.
        """
        try:
            hash_data = redis_utils.json_file_to_hash(hash_name)
            status = redis_utils.hset(hash_name, hash_data[hash_name][item_hash_field])
            return status

        except Exception as message:
            return False

    def flush(self, item="", all_items=False):
        """
        item -> string
        Removes a single item and its relations in the cache.
        If all_items is set clears all items and their relations.
        """
        try:
            cache = redis_utils.decode_bytelist(redis_utils.zrange(self.name))
            if all_items:
                for key_name in cache:
                    redis_utils.zrem(self.name, key_name)
                    redis_utils.rem_key(key_name)
                    redis_utils.hdel(key_name, item_hash_field)
            else:
                redis_utils.zrem(self.name, item)
                redis_utils.rem_key('key' + item)
                redis_utils.hdel(item, item_hash_field)

            return True

        except Exception as message:
            return False

    def release(self):
        def decorator(view_function):

            @wraps(view_function)
            def inner(*args, **kwargs):
                status = self.rem_key('key' + session['username'])
                if status:
                    session.pop('username', None)
                else:
                    abort(404)

                return view_function(*args, **kwargs)
            return inner
        return decorator

    def memorize(self):
        def decoratior(view_function):

            @wraps(view_function)
            def inner(*args, **kwargs):
                username = session['username']
                try:
                    score_to_set = redis_utils.get_set_details(self.name) + 1
                    self.set_expiration_key(username)
                    self.set_os(username, score_to_set)
                    self.set_hash(username)

                    return view_function(*args, **kwargs)

                except Exception as message:
                    abort(404)

            return inner
        return decoratior

    def is_hit(self):

        def decorator(view_function):
            @wraps(view_function)
            def inner(*args, **kwargs):
                try:
                    if session['username']:
                        key_name = 'key' + session['username']
                        redis_utils.set_expiration(key_name, self.default_expiration)
                        redis_utils.zincrby_to_highest(self.name, key_name, True)

                    return view_function(*args, **kwargs)

                except Exception as message:
                    return view_function(*args, **kwargs)

            return inner

        return decorator

    def evict(self):
        redis_info = redis_utils.get_redis_info()
        current_memory_usage = float(redis_info['used_memory'])
        max_memory = redis_info['maxmemory']
        limit = max_memory - (max_memory * 0.25)

        def decorator(fn):
            @wraps(fn)
            def inner(*args, **kwargs):
                if current_memory_usage > limit:
                    item_to_remove = redis_utils.zrange_lowest_score(self.name)
                    self.flush(item_to_remove)

                return fn(*args, **kwargs)

            return inner

        return decorator
