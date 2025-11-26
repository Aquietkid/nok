from fastapi import Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
from typing import List
import tempfile
import os

from utils.insight_face_script import verify_person
from utils.outstanding_requests import add_outstanding_req, OutstandingRequest
from utils.notification import send_notification, NotificationRequest
from utils.s3 import *
from database import db
import aiohttp
import shutil


async def download_image(url, save_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download {url}")
            content = await resp.read()
            with open(save_path, "wb") as f:
                f.write(content)
    return save_path


def get_extension_from_url(url: str):
    """
    Extract extension from URL, ignoring query params.
    Example: https://.../image.png?xyz=1 → .png
    """
    path = url.split("?")[0]
    ext = os.path.splitext(path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
        return ext
    return None


async def detect(request: Request, images: List[UploadFile] = File(...)):
    if len(images) != 2:
        return JSONResponse(
            content={"success": False,
                     "message": "Exactly 5 test images are required"},
            status_code=400,
        )

    user_id = request.state._id

    # Fetch all reference pictures of persons belonging to this user
    persons = list(db.persons.find({"user_id": str(user_id)}))

    if not persons:
        return JSONResponse(
            content={"success": False, "message": "No person images found"},
            status_code=404
        )

    # Save uploaded images temporarily
    tmp_dir = tempfile.mkdtemp()
    test_image_paths = []
    for img in images:
        tmp_path = os.path.join(tmp_dir, img.filename)
        with open(tmp_path, "wb") as f:
            f.write(await img.read())
        test_image_paths.append(tmp_path)

    # DOWNLOAD REFERENCE IMAGES (from S3 URLs in DB)
    reference_paths = []
    for p in persons:
        url = p.get("picture")
        if not url:
            continue

        ext = get_extension_from_url(url)

        # If unknown → try from content-type
        if not ext:
            ext = "jpg"

        ref_path = os.path.join(tmp_dir, f"ref_{p['_id']}.{ext}")
        await download_image(url, ref_path)
        reference_paths.append(ref_path)

    if not reference_paths:
        return JSONResponse(
            {"success": False, "message": "No valid reference images"},
            status_code=400
        )

    try:
        # Call your existing function
        result = verify_person(
            reference_paths, test_image_paths, threshold=0.5, show_results=False)

        request_id = None

        if (not result):
            user_id = request.state._id

            print("Uploading images to S3")

            # uploaded_urls = []
            # for path in test_image_paths:
            #     url = await upload_image_to_s3(path)
            #     print(f"Image uploaded to: {url}")
            #     uploaded_urls.append(url)

            uploaded_urls = []
            for img in images:
                img.file.seek(0)
                url = upload_image_to_s3(img)
                print(f"URL: {url}")
                uploaded_urls.append(url)

            print("Adding outstanding request")
            add_outstanding_req(
                local_server_user_id=user_id,
                request=OutstandingRequest(
                    images=uploaded_urls,
                    status='pending',
                    timestamp=datetime.now(timezone.utc)
                )
            )

            tokens = list(db.fcm_tokens.find({"user_id": str(user_id)}))

            for t in tokens:
                token = t.get("token")
                if token:
                    send_notification(
                        NotificationRequest(
                            token=token,
                            title="Someone is at the door",
                            body="Tap to check the visitor."
                        )
                    )

            # send_notification(NotificationRequest(token="", title="Someone is at the door", body="Click here to see who's there"))

        # For confidence, we can slightly modify verify_person to return similarity instead of just True/False
        # But since you said interface must remain same, let's simulate:

        return JSONResponse(
            content={
                "success": True,
                "match": result,
                "request_id": request_id
            }
        )
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
