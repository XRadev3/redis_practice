"""
This file contains all the functionality of the caching system.
The Cache class works with Redis as a data store.
"""
from redis_utils import redis_utils


class Cache:

    def __init__(self, default_expiration=None, name='cache'):
        """
        default_expiration: the default expiration time of a key in cache in minutes.
        name: the name of the Redis ordered_set used by the cache.
        NOTE: while the cache is empty, this ordered_set is not defined.
        """
        if default_expiration:
            self.default_expiration = default_expiration
        else:
            self.default_expiration = 120
        self.name = name

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
            return True

        except Exception as message:
            return False

    def set_expiration_key(self, key_name, expiration_time=None):
        """
        This function sets a key with expiration time.
        By default the expiration time will be set to 15 min.
        This represents a hash objects containing all the user data.
        """
        if expiration_time:
            time_to_set = expiration_time
        else:
            time_to_set = self.default_expiration

        try:
            redis_utils.set_expiration(key_name, time_to_set)
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
            redis_utils.make_persistent(key_name)
            return True

        except Exception as message:
            return False

    def rem_key(self, key_name):
        """
        This function deletes a key from the cache.
        """
        try:
            redis_utils.zrem(self.name, key_name)
            redis_utils.rem_key(key_name)

            return True

        except Exception as message:
            return False

    def flush_cache(self):
        """
        This function clears the whole ordered set in Redis where the cached users are stored.
        Also removes all active keys from Redis.
        """
        try:
            cache = redis_utils.decode_bytelist(redis_utils.zrange(self.name))
            for key_name in cache:
                redis_utils.zrem(self.name, key_name)
                redis_utils.rem_key(key_name)

            return True

        except Exception as message:
            return False
