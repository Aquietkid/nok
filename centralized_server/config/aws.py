from dotenv import load_dotenv
import os

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.getenv("AWS_REGION")
AWS_REGION = os.getenv('AWS_REGION')
