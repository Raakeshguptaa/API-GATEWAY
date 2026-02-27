from fastapi import Request
from datetime import datetime

async def log_info(request: Request, call_next):

    method = request.method
    endpoint = request.url.path
    ip_client = request.client.host 
    now = datetime.now()

    response = await call_next(request)

    status = response.status_code

    print(f"[{now}] {ip_client} {method} {endpoint} -> {status}")

    return response