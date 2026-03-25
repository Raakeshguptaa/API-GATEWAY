import time
import redis
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])

START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    redis: str


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Basic liveness check.
    Also pings Redis so you know if the rate limiter backend is reachable.
    """
    redis_status = _check_redis()
    return HealthResponse(
        status="ok",
        uptime_seconds=round(time.time() - START_TIME, 2),
        redis=redis_status,
    )


def _check_redis() -> str:
    try:
        r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=1)
        r.ping()
        return "ok"
    except Exception as e:
        return f"unreachable: {e}"