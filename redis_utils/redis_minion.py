# This python file contains the RedisMinion class.

from app.app import login
from redis_utils.redis_utils import hgetall


class RedisMinion:

    def __init__(self, hash_name=None, hash_key=None, hash_value=None, hash_map=None):
        self.hash_name = hash_name
        self.hash_key = hash_key
        self.hash_value = hash_value
        self.hash_map = hash_map

    @login.user_loader
    def load_minion(self, hash_name, hash_key):
        # Must be put it flask_utils-ish file, in order to avoid import recursion.
        return False

    def get_minion_data(self, hash_name):
        user_data = hgetall(hash_name)

        return user_data
