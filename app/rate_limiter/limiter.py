import redis
from fastapi import Request
from auth.jwt_handler import DECODED_USER_ID
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

rate_limit = 5
window_size = 10

async def add(request: Request, call_next):

    now = time.time()
    user_key = str(DECODED_USER_ID)

    request_id = getattr(request.state, "request_id", "unknown")

    #add current request 
    r.zadd(user_key, {request_id: now})

    #remove old request (outside window)
    r.zremrangebyscore(user_key,0,now - window_size)

    request_count = r.zcard(user_key)

    print("USER ID:",user_key)
    print("Request Count:", request_count)

    #check limit

    if request_count > rate_limit:
        print("overflow")

        
    response = await call_next(request)


    return response


