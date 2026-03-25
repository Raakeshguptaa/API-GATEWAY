from fastapi import Request
from fastapi.responses import JSONResponse
from rate_limiter.limiter import is_rate_limited
from auth.jwt_handler import DECODED_USER_ID


async def rate_limit_middleware(request: Request, call_next):
    user_key = str(DECODED_USER_ID)
    request_id = getattr(request.state, "request_id", "unknown")

    if is_rate_limited(user_key, request_id):
        print("overflow")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "retry_after": f"{10} seconds"
            }
        )

    return await call_next(request)