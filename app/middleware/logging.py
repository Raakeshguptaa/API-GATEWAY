from fastapi import Request
from datetime import datetime

async def log_info(request: Request, call_next):

    start_time = datetime.now()

    method = request.method
    endpoint = request.url.path
    ip_client = request.client.host

    response = await call_next(request)

    status = response.status_code

    process_time = (datetime.now() - start_time).total_seconds()

    request_id = getattr(request.state, "request_id", "unknown")

    

    #print(
        #f"[{datetime.now()}] {ip_client} {method} {endpoint} "
        #f"-> {status} time={process_time}s request_id={request_id}"
        #f" -> {request.headers.getlist}"
        
   # )

    return response