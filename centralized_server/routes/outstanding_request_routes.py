from fastapi import APIRouter
from controllers.outstanding_request_controller import *

router = APIRouter()

router.get("/all")(getAll)
router.put("/update-status")(update_status)
router.post("/get-request")(getRequest)