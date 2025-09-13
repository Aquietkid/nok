from fastapi import Request
from fastapi.responses import JSONResponse
from database import db
import os
from jose import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 1))

async def register_user(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JSONResponse(status_code=400, content={"success": False, "message": "Email and password required"})

    if db.users.find_one({"email": email}):
        return JSONResponse(status_code=400, content={"success": False, "message": "User already exists"})

    hashed_password = bcrypt.hash(password)
    db.users.insert_one({"email": email, "password": hashed_password})

    return JSONResponse(content={"success": True, "message": "User registered successfully"})

async def login_user(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = db.users.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["password"]):
        return JSONResponse(status_code=401, content={"success": False, "message": "Invalid credentials"})

    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response = JSONResponse(content={"success": True, "message": "Login successful"})
    response.headers["Authorization"] = f"Bearer {token}" 
    return response