import boto3
from PIL import Image
from Watoon import settings
import uuid
import os

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
        response = s3_client.upload_fileobj(self.file, settings.AWS_STORAGE_BUCKET_NAME, self.url)
        return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{i}'

class S3FileUploader:
    def __init__(self, file_dir, url=""):
        self.file_dir = file_dir
        self.url = url

    def upload(self):

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        cnt = 0
        for file_name in os.listdir(self.file_dir):
            file_instance = open(self.file_dir + '/' + file_name, 'rb')
            cnt += 1 
            url = self.url + "/" + str(cnt) + "." + file_name.split('.')[-1]
            s3_client.upload_fileobj(
                file_instance,
                settings.AWS_STORAGE_BUCKET_NAME, 
                url, 
                ExtraArgs={
                    "ContentType": file_name.split('.')[-1]
                })
        return cnt



class S3ImagesUploader:
    def __init__(self, url=""):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.url = url

    def upload(self, file_dir, file_name ):        
        file_instance = open(file_dir + "/" + file_name, 'rb')
        url = self.url + "/" + file_name
        self.s3_client.upload_fileobj(
            file_instance,
            settings.AWS_STORAGE_BUCKET_NAME, 
            url, 
            ExtraArgs={
                "ContentType": file_name.split('.')[-1]
            })
        return f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/', url