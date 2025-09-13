from fastapi import Request
from fastapi.responses import JSONResponse
import os
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

async def verify_token(request: Request, call_next):
    if request.url.path.startswith("/api/auth"): 
        return await call_next(request)

    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"success": False, "message": "Missing or invalid token"})

    try:
        jwt.decode(token.replace("Bearer ", ""), SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"success": False, "message": "Token expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid token"})

    return await call_next(request)