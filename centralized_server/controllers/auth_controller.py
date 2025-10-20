from fastapi import Request
from fastapi.responses import JSONResponse
from database import db
from jose import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from config.jwt import *
from bson import ObjectId


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
        "_id": str(user.get("_id")),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    user["_id"] = str(user["_id"])
    user.pop("password", None)

    response = JSONResponse(
        content={"success": True, "data": {"token": token, "user": user}})
    return response


async def authenticate(request: Request):
    user_id = request.state._id

    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        return JSONResponse(content={"success": False, "error": "User not found"}, status_code=404)
    
    user["_id"] = str(user["_id"])
    user.pop("password", None)

    response = JSONResponse(
        content={"success": True, "data": {"user": user}})
    return response
