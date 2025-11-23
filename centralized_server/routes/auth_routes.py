from fastapi import APIRouter
from controllers.auth_controller import *

router = APIRouter()

router.post("/register")(register_user)
router.post("/login")(login_user)
router.get("/authenticate")(authenticate)
