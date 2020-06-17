"""
This file contains all the functionality of the caching system.
The Cache class works with Redis as a data store.
"""
import os
import json
import logging
import subprocess


from functools import wraps
from flask import session, make_response, redirect
from redis_utils import redis_utils


class Cache:
    current_name = str()
    is_cleaning = False

    def __init__(self, storage_file, key_prefix='key_', name='cache', item_hash_field='attributes', default_expiration=1800):
        """
        default_expiration: the default expiration time of a key in cache in minutes.
        name: the name of the Redis ordered set used by the cache.
        key_prefix: prefix to the expiration key.
        item_hash_field: static key pointing to the nested dict in the hash.
        (hash -> {'hash_key': {'item_hash_field': {your_data}}})
        NOTE: while the cache is empty, this ordered set is not defined.
        """
        self.name = name
        self.default_expiration = default_expiration
        self.key_prefix = key_prefix
        self.item_hash_field = item_hash_field
        self.storage_file = storage_file

        if not self.is_cleaning:
            path = os.getcwd() + '/../application/cache_cleaner.py'

            subprocess.Popen(
                ['python3', path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            self.is_cleaning = True

    def get_cache(self):
        """
        This function returns all hash keys currently active in the cache in a list.
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
            logging.log(logging.ERROR, str(message))
            return message

    def set_os(self, key, score):
        """
        Arguments to create a ordered_set: set name, key name, key value.
        The same way we add a key to a ordered_set.
        """
        try:
            redis_utils.zadd(self.name, key, score)
            redis_utils.zrange(self.name)
            return True

        except Exception as message:
            logging.log(logging.ERROR, str(message))
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
            redis_utils.set_key(self.key_prefix + session['username'], key_value, time_to_set)
            return True

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            return False

    def get_expiration_key(self, key, time_only=False):
        """
        This function returns a active key and its expiration time.
        If time_only is set, return the expiration time left on the key as a string.
        Else if it is successful, it will return they key name and expiration time as a list.
        """
        try:
            key = self.key_prefix + key
            if time_only:
                return redis_utils.get_expiration_time(key)

            else:
                exp_time = redis_utils.get_expiration_time(key)
                key = redis_utils.get_key(key)
                return [exp_time, key]

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            return False

    def make_key_persistent(self):
        """
        This function makes a key persistent. In other words, removes its expiration time.
        """
        try:
            key = self.key_prefix + session['username']
            status = redis_utils.make_persistent(key)
            return status

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            return False

    def rem_key(self, username):
        """
        This function deletes a key and it's instance in the ordered set as well as the hash data.
        """
        try:
            key = self.key_prefix + username
            redis_utils.zrem(self.name, username)
            redis_utils.rem_key(key)
            redis_utils.hdel(username, self.item_hash_field)

            return True

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            return False

    def set_hash(self, hash_name):
        """
        This function reads the key data from the storage by its hash_name.
        If successful it will create a Redis hash object that will hold the read data.
        If unsuccessful it will return False.
        """
        try:
            with open(self.storage_file, 'r') as input_file:
                for line in input_file:
                    if line == '\n':
                        pass

                    elif hash_name in line:
                        data_to_set = json.loads(line)
                        break

                redis_utils.hset(hash_name, data_to_set[hash_name][self.item_hash_field])
                return True

        except Exception as message:
            logging.log(logging.ERROR, str(message))
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
                for username in cache:
                    key = self.key_prefix + username
                    redis_utils.zrem(self.name, username)
                    redis_utils.rem_key(key)
                    redis_utils.hdel(username, self.item_hash_field)
            else:
                key = self.key_prefix + item
                redis_utils.zrem(self.name, item)
                redis_utils.rem_key(key)
                redis_utils.hdel(item, self.item_hash_field)

            return True

        except Exception as message:
            logging.log(logging.ERROR, str(message))
            return False

    def release(self):
        """
        This decorator removes all the items related to the cached data(sessions/keys/hash/zset).
        """

        def decorator(fn):

            @wraps(fn)
            def inner(*args, **kwargs):
                if self.rem_key(session['username']):
                    session.pop('username', None)
                else:
                    redirect("/", 404)

                return fn(*args, **kwargs)
            return inner
        return decorator

    def memorize(self):
        """
        This decorator sets:
            - expiration_key
            - hash data
            - adds a value related to the exp. key in the cache zset.
        """
        def decoratior(fn):

            @wraps(fn)
            def inner(*args, **kwargs):
                username = session['username']
                if not redis_utils.get_key(self.key_prefix + username):
                    try:
                        score_to_set = redis_utils.get_ordered_set_details(self.name) + 1
                        self.set_expiration_key(username)
                        self.set_os(username, score_to_set)
                        self.set_hash(username)

                        return fn(*args, **kwargs)

                    except Exception as message:
                        return redirect('/', 404, )

                return fn(*args, **kwargs)
            return inner
        return decoratior

    def is_hit(self):
        """
        This decorator returns the expiration_key value to default.
        Also increments the score of the value in the zset to the highest.
        """
        def decorator(fn):
            @wraps(fn)
            def inner(*args, **kwargs):
                try:
                    if session['username']:
                        key = self.key_prefix + session['username']
                        redis_utils.set_expiration(key, self.default_expiration)
                        redis_utils.zincrby_to_highest(self.name, redis_utils.get_key(key), True)

                    return fn(*args, **kwargs)

                except Exception as message:
                    logging.log(logging.ERROR, str(message))
                    return fn(*args, **kwargs)

            return inner

        return decorator

    def evict(self):
        """
        This decorator evicts the value in the cache zset with the lowest score
        and its relations when 75% of the max memory is reached.
        """
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

    def update(self, data_to_set):
        """
        This decorator updates the value of the cached hash data.
        NOTE! New data must be written in the data storage first.
        """
        def decorator(fn):
            @wraps(fn)
            def inner(*args, **kwargs):
                username = session['username']
                key = self.key_prefix + username

                redis_utils.set_expiration(key, self.default_expiration)
                redis_utils.zincrby_to_highest(self.name, key, True)
                self.set_hash(username)

                return fn(*args, **kwargs)

            return inner

        return decorator
