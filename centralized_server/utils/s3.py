import boto3, uuid, mimetypes
from botocore.exceptions import NoCredentialsError
from config.aws import *

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
        raise Exception("S3 credentials not configured correctly")


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
