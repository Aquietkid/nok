import cv2
import time
import requests
from ultralytics import YOLO
import insightface
from io import BytesIO
import os

from dotenv import load_dotenv

load_dotenv()

POLLING_API =  "http://13.60.56.52/api/polling/register"

model = YOLO("local_server/yolov8n-face-lindevs.pt")

face_app = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

last_request_time = 0  # cooldown timer
polling_active = False

def start_polling():
    global polling_active
    polling_active = True
    start_time = time.time()

    while time.time() - start_time < 120:
        try:
            r = requests.get(POLLING_API, timeout=5)
            data = r.json()
            if data.get("true") is True:
                print("Calling ESP32 API here")
                requests.post("http://10.126.43.3/open", timeout=10)
                polling_active = False
                return {"result": "success"}
        except:
            pass

        time.sleep(2)

    polling_active = False
    return {"result": "timeout"}


def process_faces():
    global last_request_time

    if polling_active:
        return {"error": "Server polling. Please wait"}

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

    headers = {
       "Authorization": f"Bearer {os.getenv("BEARER")}"
    }

    print(headers)

    try:
        resp = requests.post("http://13.60.56.52:8000/api/detect/detect", files=files, timeout=15, headers=headers)
        # resp = requests.post("{base_url}/api/detect/detect", files=files, timeout=15)
        # resp = requests.post("http://localhost:8000/api/detect/detect", files=files, timeout=15, headers=headers)
        last_request_time = time.time()
        response = resp.json()

        print("Response: ", response)
        
        if response['match']:
            return {"result": "yes"}
        
    except Exception as e:
        print(f"Error! Failed to contact detection API: {e}")
        return {"error": f"Failed to contact detection API: {str(e)}"}

    polling_result = start_polling()
    return {"result": "no"}