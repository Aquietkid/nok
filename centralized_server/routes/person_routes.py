from fastapi import APIRouter
from controllers.person_controller import *

router = APIRouter()

# router.ad
router.post("/add")(add_person)
router.get("/")(get_all_persons)
router.put("/edit/{person_id}")(edit_person)
router.delete("/{person_id}")(delete_person)
