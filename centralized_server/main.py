import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from middlewares.error_handler import error_handler
from middlewares.auth_middleware import verify_token
from routes import auth_routes

load_dotenv()

PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

app.middleware("http")(error_handler)
app.middleware("http")(verify_token)

@app.get("/")
async def root():
    return {
        "success": True,
        "message": f"🚀 Centralized Server is running on port {PORT}",
        "docs": "/docs"
    }

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
