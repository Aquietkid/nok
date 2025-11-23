from fastapi import APIRouter
from controllers.fcm_controller import *

router = APIRouter()

router.post("/save_fcm")(save_fcm_token)
