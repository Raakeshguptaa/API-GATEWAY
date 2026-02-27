from fastapi import FastAPI, Request
from routes import client, admin
from middleware.request_id import add_request_id
from middleware.logging import log_info

app = FastAPI()

app.include_router(client.router)
app.include_router(admin.route)

app.middleware("http")(log_info)
app.middleware("http")(add_request_id)


@app.get('/')
def homepage(request: Request):
    return {
        "message": "Request processed",
        "request_id": request.state.request_id,
        "method":request.method
    }