from flask import Blueprint, jsonify
from controllers.face_controller import process_faces

face_bp = Blueprint("face_routes", __name__)

@face_bp.route("/check", methods=["GET"])
def check():
    result = process_faces()
    return jsonify(result)
