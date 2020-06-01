#!/usr/bin/env python3

import redis

set_name = "cache"
key_pattern = "k*"
hash_field = "attributes"

redis_client = redis.StrictRedis()
all_keys_in_set = redis_client.zrange(set_name, 0, -1)
all_keys = redis_client.keys(key_pattern)
all_key_values = redis_client.mget(all_keys)
num_keys, num_keys_set = len(all_keys), len(all_keys_in_set)

if num_keys == num_keys_set:
    quit()

for key in all_keys_in_set:
    if key not in all_key_values:
        redis_client.zrem(set_name, key)
        redis_client.hdel(key.decode(), hash_field)

