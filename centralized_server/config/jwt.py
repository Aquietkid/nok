from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", 1))