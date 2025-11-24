import os
from dotenv import load_dotenv
from fastapi import FastAPI
import config.firebase
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

from middlewares.error_handler import error_handler
from middlewares.auth_middleware import verify_token
from routes import auth_routes, person_routes, fcm_routes, detection_routes, outstanding_request_routes
from utils.notification import send_notification, NotificationRequest

load_dotenv()

PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    # send_notification(NotificationRequest(
    #     body="This is a test notification", title="Testing Ding Dong!", token="e1RfKhJOQ7GZkztLR_2FNI:APA91bHSeeU5VUCmlof2M2llKc1vrDt393Ta3DshGH51KiJZLInKOQXaWdJ54Gm26XXUFupGDBzah-z3creO07OFaxfkgTOXetvgwaPJUXogv_mUaQQ15-Y"))
    return {
        "success": True,
        "message": f"🚀 Centralized Server is running on port {PORT}",
        "docs": "/docs"
    }

app.middleware("http")(error_handler)
app.middleware("http")(verify_token)

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(detection_routes.router, prefix="/api/detect", tags=["Detect"])
app.include_router(outstanding_request_routes.router, prefix="/api/polling", tags=["Polling"])
app.include_router(person_routes.router, prefix="/api/person", tags=["Person"])
app.include_router(fcm_routes.router, prefix="/api/fcm", tags=["FCM"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
