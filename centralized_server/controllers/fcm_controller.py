from fastapi import Request
from fastapi.responses import JSONResponse
from database import db
from config.jwt import *
from bson import ObjectId

async def save_fcm_token(request: Request):
    user_id = request.state._id
    data = await request.json()
    token = data.get("token") 
    
    if not token:
        return JSONResponse(
            content={"success": False, "message": "Token missing"},
            status_code=400
        )

    # Upsert (update if exists, otherwise insert)
    db.fcm_tokens.update_one(
        {"user_id": user_id},                     # find record for this user
        {"$set": {"token": token}},               # update token
        upsert=True                               # insert if not exists
    )
    
    response = JSONResponse(
        content={"success": True})
    
    return response