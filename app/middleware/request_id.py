import uuid
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_request_id(request: Request, call_next):

    #check if already have request_id in header
    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid.uuid4())
        request.state.user_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

@app.get("/")
async def root(request: Request):
    return {
        "message": "Request processed",
        "request_id": request.state.user_id
    }

        
    
