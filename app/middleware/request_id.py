# middleware/request_id.py

import uuid
from datetime import datetime
from fastapi import Request


async def add_request_id(request: Request, call_next):

    # Check if already have request_id in header
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())

    # Always store it
    request.state.request_id = request_id

    # Continue request
    response = await call_next(request)

    # Always set header
    response.headers["X-Request-ID"] = request_id


    return response
