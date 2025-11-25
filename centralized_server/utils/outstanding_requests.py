from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from utils.s3_utils import delete_image_from_s3


class OutstandingRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="Unique ID for the request")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow(), description="Time when request was created")
    images: List[str] = Field(..., description="List of image URLs")
    status: str = Field(
        "pending", description="Status of the request, e.g., 'pending', 'approved', 'denied'")


# Dictionary keyed by local server ID
OutstandingRequestsDict = Dict[str, List[OutstandingRequest]]
outstanding_requests: OutstandingRequestsDict = {}


# Add a new request
def add_outstanding_req(local_server_user_id: str, request: OutstandingRequest):
    if local_server_user_id not in outstanding_requests:
        outstanding_requests[local_server_user_id] = []
    outstanding_requests[local_server_user_id].append(request)
    return request.request_id


# Remove a specific outstanding request for a local server by request_id.
def remove_outstanding_req(local_server_user_id: str, request_id: str):
    if local_server_user_id in outstanding_requests:
        requests = outstanding_requests[local_server_user_id]

        for r in requests:
            if r.request_id == request_id:
                for url in r.images:
                    delete_image_from_s3(url)
                break

        # Keep only requests that do not match the request_id
        remaining_requests = [
            r for r in requests if r.request_id != request_id]
        if remaining_requests:
            outstanding_requests[local_server_user_id] = remaining_requests
        else:
            # If no requests remain, remove the key entirely
            del outstanding_requests[local_server_user_id]


# Get all requests for a local server
def get_outstanding_requests(local_server_user_id: str) -> List[OutstandingRequest]:
    return outstanding_requests.get(local_server_user_id, [])


def get_outstanding_request(local_server_user_id: str, request_id: str) -> OutstandingRequest | None:
    all_requests = outstanding_requests.get(local_server_user_id, [])

    for req in all_requests:
        if req.request_id == request_id:
            return req

    return None

# Update a specific request by request_id
def update_request(local_server_user_id: str, request_id: str, status: str) -> bool:
    for req in outstanding_requests.get(local_server_user_id, []):
        if req.request_id == request_id:
            req.status = status
            return True
    return False
