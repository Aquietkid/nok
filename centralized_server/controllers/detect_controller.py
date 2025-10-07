from fastapi import Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List
import tempfile
import os

from utils.insight_face_script import verify_person


# Reference images folder (for now, local)
REFERENCE_DIR = "temp_ref_img"

# Collect all valid image files from the folder
REFERENCE_PATHS = [
    os.path.join(REFERENCE_DIR, f)
    for f in os.listdir(REFERENCE_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]


async def detect(request: Request, images: List[UploadFile] = File(...)):
    if len(images) != 5:
        return JSONResponse(
            content={"success": False,
                     "message": "Exactly 5 test images are required"},
            status_code=400,
        )

    # Save uploaded images temporarily
    tmp_dir = tempfile.mkdtemp()
    test_image_paths = []
    for img in images:
        tmp_path = os.path.join(tmp_dir, img.filename)
        with open(tmp_path, "wb") as f:
            f.write(await img.read())
        test_image_paths.append(tmp_path)

    try:
        # Call your existing function
        result = verify_person(
            REFERENCE_PATHS, test_image_paths, threshold=0.4, show_results=False)

        # For confidence, we can slightly modify verify_person to return similarity instead of just True/False
        # But since you said interface must remain same, let's simulate:

        return JSONResponse(
            content={
                "success": True,
                "match": result
            }
        )
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    finally:
        # cleanup tmp images
        for path in test_image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(tmp_dir)
