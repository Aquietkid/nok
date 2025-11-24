from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from config.jwt import *

async def verify_token(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)

    # if not request.url.path.startswith("/api/auth/authenticate"):
        # if request.url.path.startswith("/api/auth"):
            # return await call_next(request)

    path = request.url.path

    if path.startswith("/api/auth"):
        return await call_next(request)

    print("Checking token")

    token = request.headers.get("Authorization")
    print(f"Token: {token}")

    if not token or not token.startswith("Bearer "):
        print("Token not found")
        return JSONResponse(status_code=401, content={"success": False, "message": "Missing or invalid token"})

    try:
        print("Trying to extract JWT")

        token = token.replace("Bearer ", "").strip()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("_id")

        print(f"JWT Extracted. \nToken: {token}\nPaylaod: {payload}\nUSER_ID: {user_id}")


        if not user_id:
            print("USER_ID not found!")
            return JSONResponse(status_code=401, content={
                "success": False,
                "message": "Invalid token payload"
            })
            
        request.state._id = user_id

    except jwt.ExpiredSignatureError:
        print(f"Token Expired!")
        return JSONResponse(status_code=401, content={"success": False, "message": "Token expired"})
    except jwt.InvalidTokenError:
        print(f"Token Invalid!")
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid token"})

    print("Calling next middleware")
    return await call_next(request)
