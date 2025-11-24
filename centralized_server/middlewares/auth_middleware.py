from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from config.jwt import *

async def verify_token(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)

    if not request.url.path.startswith("/api/auth/authenticate"):
        if request.url.path.startswith("/api/auth"):
            return await call_next(request)

    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"success": False, "message": "Missing or invalid token"})

    try:
        token = token.replace("Bearer ", "").strip()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # user_id = payload.get("_id")
        user = payload.get("user", {})
        user_id = user.get("_id")


        if not user_id:
            return JSONResponse(status_code=401, content={
                "success": False,
                "message": "Invalid token payload"
            })
            
        request.state._id = user_id

    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"success": False, "message": "Token expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid token"})

    return await call_next(request)
