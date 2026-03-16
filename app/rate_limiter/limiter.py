import redis
from fastapi import Request
from auth.jwt_handler import DECODED_USER_ID
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


async def add(request: Request, call_next):

    now = time.time()

    request_id = getattr(request.state, "request_id", "unknown")

    r.zadd(str(DECODED_USER_ID), {request_id: now})

    sortedset = r.zrangebyscore(str(DECODED_USER_ID), 0, now, withscores=True)

    print("User ID:", DECODED_USER_ID)
    print("Redis data:", sortedset)

    response = await call_next(request)

    return response