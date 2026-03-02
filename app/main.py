from fastapi import FastAPI, Request

from routes import client, admin
from middleware.request_id import add_request_id
from middleware.logging import log_info
from auth.middleware import auth_middleware


app = FastAPI()

# Routers
app.include_router(client.router)



# Middleware registration (reverse execution order)
app.middleware("http")(auth_middleware)
app.middleware("http")(log_info)
app.middleware("http")(add_request_id)


@app.get("/")
def homepage(request: Request):
    return {
        "message": "Request processed",
        "request_id": request.state.request_id
    }