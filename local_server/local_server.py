from flask import Flask, jsonify
from routes.face_routes import face_bp

HOST = "0.0.0.0"
PORT = 5000

app = Flask(__name__)

app.register_blueprint(face_bp)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
