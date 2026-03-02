from fastapi import Request
from fastapi.responses import JSONResponse

from .jwt_handler import verify_token
from .api_key import validate_api_key


async def auth_middleware(request: Request, call_next):

    # default state values
    request.state.user = None
    request.state.service = None
    request.state.auth_type = None

    

    auth_header = request.headers.get("Authorization")
    api_key = request.headers.get("x-api-key")
    





    # JWT authentication
    if auth_header and auth_header.startswith("Bearer "):

        token = auth_header.split(" ")[1]

        try:
            payload = verify_token(token)

            if payload:
                request.state.user = payload
                request.state.auth_type = "jwt"

        except Exception:
            pass

    # API key authentication
    elif api_key:

        if validate_api_key(api_key):
            request.state.service = api_key
            request.state.auth_type = "api_key"

    # Unauthorized
    if not request.state.user and not request.state.service:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )

    response = await call_next(request)

    return response

