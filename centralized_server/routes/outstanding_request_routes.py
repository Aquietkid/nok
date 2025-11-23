from fastapi import APIRouter
from controllers.outstanding_request_controller import *

router = APIRouter()

router.post("/register")(add)