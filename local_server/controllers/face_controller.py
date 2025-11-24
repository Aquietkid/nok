import cv2
import time
import requests
from ultralytics import YOLO
import insightface
from io import BytesIO

model = YOLO("yolov8n-face-lindevs.pt")
face_app = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

last_request_time = 0  # cooldown timer

def process_faces():
    global last_request_time

    if time.time() - last_request_time < 5:
        return {"error": "Cooldown active. Try again later."}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"error": "Camera not accessible"}

    frames_with_faces = 0
    captured_frames = []

    while frames_with_faces < 5:
        success, frame = cap.read()
        if not success:
            continue

        results = model(frame, verbose=False)
        detections = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes else []

        if len(detections) > 0:
            frames_with_faces += 1
            _, buffer = cv2.imencode(".jpg", frame)
            captured_frames.append(BytesIO(buffer))

    cap.release()

    # Prepare files for POST request
    files = [(f"images", ("frame.jpg", f.getvalue(), "image/jpeg")) for i, f in enumerate(captured_frames)]

    try:
        resp = requests.post("http://13.60.56.52:8000/api/detect/detect", files=files, timeout=15)
        # resp = requests.post("http://localhost:8000/api/detect/detect", files=files, timeout=15)
        last_request_time = time.time()
        response = resp.json()
        print("Response: ", response)
        if response['match']:
            return {"result": "yes"}
        # return resp.json()
    except Exception as e:
        print("Error")
        return {"error": f"Failed to contact detection API: {str(e)}"}

    return {"result": "no"}