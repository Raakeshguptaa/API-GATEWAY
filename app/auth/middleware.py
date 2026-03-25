from fastapi import Request
from fastapi.responses import JSONResponse

from .jwt_handler import verify_token
from .api_key import validate_api_key , validate_admin_key



# Paths that should never require auth
EXEMPT_PATHS = {
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/health",
    "/api/auth/login",
    "/api/auth/refresh",
}

async def auth_middleware(request: Request, call_next):

    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)


    # default state values
    request.state.user = None
    request.state.service = None
    request.state.auth_type = None
    request.state.is_admin = False

    

    auth_header = request.headers.get("Authorization")
    api_key = request.headers.get("x-api-key")
    admin_key = request.headers.get("admin-api-key")
    

    is_admin_route = request.url.path.startswith("/admin")
    
    





    # JWT authentication
    if auth_header and auth_header.startswith("Bearer "):

        token = auth_header.split(" ")[1]

        print(auth_header)



        try:
            
            payload = verify_token(token)

        


            if payload:
                request.state.user = payload
                request.state.auth_type = "jwt"

                

        except Exception:
        
            pass

    elif admin_key and validate_admin_key(admin_key):
        request.state.service = admin_key
        request.state.auth_type = "admin_key"
        request.state.is_admin = True

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
    
    if is_admin_route and not request.state.is_admin:
        return JSONResponse(status_code=403, content={"error":"forbidden: Admin access required"})

    response = await call_next(request)

    return response

