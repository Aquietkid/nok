from fastapi import APIRouter
from controllers.detect_controller import detect

router = APIRouter()

router.post("/detect")(detect)
