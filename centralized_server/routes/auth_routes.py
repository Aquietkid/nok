from fastapi import APIRouter
from controllers.auth_controller import register_user, login_user

router = APIRouter()

router.post("/register")(register_user)
router.post("/login")(login_user)
