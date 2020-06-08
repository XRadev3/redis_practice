#!/usr/bin python3

import os
import time
import redis
import datetime
import logging

set_name = "cache"
key_pattern = "key*"
hash_field = "attributes"
log_path = os.getcwd() + '/../cache_cleaner.log'
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    filename=log_path,
                    level=logging.DEBUG)

logging.log(logging.INFO, "LOG CLEANER INITIATED!")


redis_client = redis.StrictRedis()


while True:
    try:
        now = datetime.datetime.now()
        if not now.second:
            all_keys_in_set = redis_client.zrange(set_name, 0, -1)
            all_keys = redis_client.keys(key_pattern)
            all_key_values = redis_client.mget(all_keys)
            num_keys, num_keys_set = len(all_keys), len(all_keys_in_set)

            if num_keys == num_keys_set:
                pass

            else:
                for key in all_keys_in_set:
                    if key not in all_key_values:
                        redis_client.zrem(set_name, key)
                        redis_client.hdel(key.decode(), hash_field)
                        logging.log(logging.INFO, "Cache cleaner -> {}'s data has been cleared.".format(key.decode()))

            logging.log(logging.INFO, "Cache sweep done. Next sweep in 60 seconds.")
            time.sleep(1)

        else:
            time.sleep(60-now.second)

    except Exception as message:
        logging.log(logging.ERROR, message)
        pass
