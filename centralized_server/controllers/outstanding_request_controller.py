from fastapi import Request
from fastapi.responses import JSONResponse
import json
from config.jwt import *
from bson import ObjectId
from utils.outstanding_requests import *


from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils.outstanding_requests import get_outstanding_requests, update_request, remove_outstanding_req


# Schema for update payload
class UpdateStatusPayload(BaseModel):
    request_id: str
    status: str  # "approved" or "denied"


async def getAll(request: Request):
    user_id = request.state._id

    outstanding_req = get_outstanding_requests(user_id)

    serialized_reqs = [
        json.loads(req.model_dump_json()) for req in outstanding_req
    ]

    response = JSONResponse(
        content={"success": True, "data": serialized_reqs})
    return response


async def update_status(request: Request, payload: UpdateStatusPayload):
    user_id = request.state._id

    if payload.status not in ["approved", "denied"]:
        return JSONResponse(content={"success": False, "message": "Invalid status"}, status_code=400)

    if payload.status == "approved":
        updated = update_request(user_id, payload.request_id, payload.status)
        if not updated:
            return JSONResponse(content={"success": False, "message": "Request not found"}, status_code=404)
    elif payload.status == "denied":
        remove_outstanding_req(user_id, payload.request_id)

    return JSONResponse(content={"success": True})
