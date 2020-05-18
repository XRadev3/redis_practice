# This python file contains the RedisMinion class.
from redis_utils import redis_utils


class RedisMinion:

    def __init__(self, hash_name, hash_key, hash_value=None, hash_map=None):
        self.hash_name = hash_name
        self.hash_key = hash_key
        self.hash_value = hash_value
        self.hash_map = hash_map

    def update_minion(self, hash_value=None, hash_map=None, auto=True):
        try:
            if auto:
                self.hash_value = redis_utils.hget(self.hash_name, self.hash_key)
            else:
                self.hash_value = hash_value
            return True

        except Exception as msg:
            return False

    def get_minion_key(self, hash_key):
        return redis_utils.hget_from_all(hash_key)


