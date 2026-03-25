import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

RATE_LIMIT = 5
WINDOW_SIZE = 10


def is_rate_limited(user_key: str, request_id: str) -> bool:
    now = time.time()

    # add current request
    r.zadd(user_key, {request_id: now})

    # remove requests outside the window
    r.zremrangebyscore(user_key, 0, now - WINDOW_SIZE)

    request_count = r.zcard(user_key)

    print("USER ID:", user_key)
    print("Request Count:", request_count)

    return request_count > RATE_LIMIT