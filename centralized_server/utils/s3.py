import boto3, uuid, mimetypes, os, sys
from botocore.exceptions import NoCredentialsError
from config.aws import *
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET")

print("--- AWS CONFIG DEBUG ---")
# print(f"Env Loaded: {loaded} (Path: {env_path})")
print(f"Access Key: {'OK' if AWS_ACCESS_KEY_ID else 'None'}")
print(f"Secret Key: {'OK' if AWS_SECRET_ACCESS_KEY else 'None'}")
print(f"Region:     {AWS_REGION}")
print(f"Bucket:     {BUCKET_NAME}")
print("------------------------")

# Stop execution immediately if any credential is missing
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME]):
    print("ERROR: One or more AWS environment variables are missing (None).")
    # This prevents the obscure 'NoneType' error later
    sys.exit(1)

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_image_to_s3(file):
    file_ext = mimetypes.guess_extension(file.content_type)
    filename = f"{uuid.uuid4()}{file_ext or ''}"
    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": file.content_type}
        )
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
    except NoCredentialsError:
        print("ERROR! S3 credentials not configured correctly")
        raise Exception("S3 credentials not configured correctly")

# def upload_image_to_s3(file):

#     content_type = getattr(file, "content_type", None) or "image/jpeg"
#     print(content_type)
#     file_ext = mimetypes.guess_extension(content_type) or ".jpg"
#     print(f"Content Type: {content_type}\tFile Extension: {file_ext}")
#     filename = f"{uuid.uuid4()}{file_ext}"
#     print(f"Filename: {filename}")
#     print(f"File type: {type(file)}")

#     try:
#         print("Initiating upload image to S3")
#         s3.upload_fileobj(
#             file.file,
#             BUCKET_NAME,
#             filename,
#             ExtraArgs={"ContentType": content_type}
#         )
#     except Exception as e:
#         print(f"Error uploading to S3: {e}")
#         raise

#     return f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{filename}"


def delete_image_from_s3(image_url: str):
    """
    Deletes an image from S3 using its public URL.
    """
    # Extract filename from URL
    filename = image_url.split("/")[-1]
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        print(f"Deleted old image from S3: {filename}")
    except Exception as e:
        print(f"Error deleting image from S3: {e}")
