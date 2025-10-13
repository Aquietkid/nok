from fastapi import Request, UploadFile, Form
from fastapi.responses import JSONResponse
from database import db
from utils.s3 import upload_image_to_s3, delete_image_from_s3
from bson import ObjectId


async def add_person(request: Request, name: str = Form(...), picture: UploadFile = None):
    _id = getattr(request.state, "_id", None)
    if not _id:
        return JSONResponse({"error": "Missing user ID"}, status_code=401)

    # Upload picture to S3
    image_url = None
    if picture:
        image_url = upload_image_to_s3(picture)
    
    person_data = {
        "user_id": _id,
        "name": name,
        "picture": image_url
    }

    result = db.persons.insert_one(person_data)

    # Convert ObjectId to string before returning
    person_data["_id"] = str(result.inserted_id)
    person_data["user_id"] = str(person_data["user_id"])  # if _id is also an ObjectId

    return JSONResponse({
        "success": True,
        "message": "Person added successfully",
        "data": person_data
    })

async def get_all_persons(request: Request):
    _id = getattr(request.state, "_id", None)
    if not _id:
        return JSONResponse({"success": False, "message": "Missing user ID"}, status_code=401)

    # Fetch all persons for this user
    persons_cursor = db.persons.find({"user_id": _id})
    persons = list(persons_cursor)

    # Convert ObjectIds to strings
    for person in persons:
        person["_id"] = str(person["_id"])
        person["user_id"] = str(person["user_id"])

    return JSONResponse({
        "success": True,
        "message": "Authorized persons fetched successfully",
        "data": persons
    })

async def edit_person(request: Request, person_id: str, name: str = Form(None), picture: UploadFile = None):
    _id = getattr(request.state, "_id", None)
    if not _id:
        return JSONResponse({"success": False, "message": "Missing user ID"}, status_code=401)

    # Ensure at least one field is provided
    if not name and not picture:
        return JSONResponse({"success": False, "message": "Name or picture required"}, status_code=400)

    # Fetch the person record and verify ownership
    print(person_id, _id)
    person = db.persons.find_one({"_id": ObjectId(person_id), "user_id": _id})
    if not person:
        return JSONResponse({"success": False, "message": "Person not found or unauthorized"}, status_code=404)

    update_fields = {}

    # Update name if provided
    if name:
        update_fields["name"] = name

    # Handle image replacement
    if picture:
        # Delete previous image from S3 if exists
        if person.get("picture"):
            try:
                delete_image_from_s3(person["picture"])
            except Exception as e:
                print("Warning: Failed to delete old image:", e)

        # Upload new image
        new_image_url = upload_image_to_s3(picture)
        update_fields["picture"] = new_image_url

    # Perform the update
    db.persons.update_one({"_id": ObjectId(person_id)}, {"$set": update_fields})

    # Prepare updated document for response
    updated_person = db.persons.find_one({"_id": ObjectId(person_id)})
    updated_person["_id"] = str(updated_person["_id"])
    updated_person["user_id"] = str(updated_person["user_id"])

    return JSONResponse({
        "success": True,
        "message": "Person updated successfully",
        "data": updated_person
    })

async def delete_person(request: Request, person_id: str):
    _id = getattr(request.state, "_id", None)
    if not _id:
        return JSONResponse({"success": False, "message": "Missing user ID"}, status_code=401)

    # Check if the record exists and belongs to the user
    person = db.persons.find_one({"_id": ObjectId(person_id), "user_id": _id})
    if not person:
        return JSONResponse({"success": False, "message": "Person not found or unauthorized"}, status_code=404)

    # Delete image from S3 if exists
    if person.get("picture"):
        try:
            delete_image_from_s3(person["picture"])
        except Exception as e:
            print("Warning: Failed to delete image from S3:", e)

    # Delete record from database
    db.persons.delete_one({"_id": ObjectId(person_id)})

    return JSONResponse({
        "success": True,
        "message": "Person deleted successfully"
    })