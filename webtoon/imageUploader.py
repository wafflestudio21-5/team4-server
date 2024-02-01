import boto3
from PIL import Image
from Watoon import settings
import uuid

class S3ImageUploader:
    def __init__(self, file, url=""):
        self.file = file
        self.url = url

    def upload(self):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        i = self.url #+ "/" + str(uuid.uuid4())
        response = s3_client.upload_fileobj(self.file, settings.AWS_STORAGE_BUCKET_NAME, i)
        return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{i}'

