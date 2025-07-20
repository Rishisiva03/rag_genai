from fastapi import APIRouter, UploadFile, File

from app.config import UPLOAD_FOLDER_PATH, METADATA_FILE_PATH
import os
import uuid
from datetime import datetime
import fsspec
router = APIRouter(prefix="/upload")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
from fastapi import UploadFile, File, APIRouter
from datetime import datetime
from botocore.config import Config as BotoConfig
import fsspec
import hashlib
import os


import boto3
from botocore.config import Config
from io import BytesIO

def upload_content_to_s3_with_v4(file_content: bytes, s3_path: str, bucket_name: str,
                                 access_key: str, secret_key: str, region: str) -> str:
    boto_config = Config(signature_version='s3v4')

    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    s3 = session.client("s3", config=boto_config)
    file_stream = BytesIO(file_content)

    s3.upload_fileobj(
        Fileobj=file_stream,
        Bucket=bucket_name,
        Key=s3_path
    )

    s3_url = f"s3://{bucket_name}/{s3_path}"
    print(f"File uploaded to S3: {s3_url}")
    return s3_url



@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        return {"error": "File is empty"}

    print(f"Received file: {file.filename}, size: {len(contents)} bytes")
    await file.close()

    if UPLOAD_FOLDER_PATH.startswith("s3://"):
        file_path = f"{UPLOAD_FOLDER_PATH}/{file.filename}"
        storage_options = {
            "key": AWS_ACCESS_KEY_ID,
            "secret": AWS_SECRET_ACCESS_KEY,
            "client_kwargs": {
                "region_name": "ap-south-1",
                # "config": boto_config
            }
        }
        fs = fsspec.filesystem('s3', **storage_options)
        print(f"Saving file to: {file_path}")
        upload_content_to_s3_with_v4(
            file_content=contents,
            s3_path='/'.join(file_path.split('/')[3:]),
            bucket_name=UPLOAD_FOLDER_PATH.split('/')[2],
            access_key=AWS_ACCESS_KEY_ID,
            secret_key=AWS_SECRET_ACCESS_KEY,
            region="ap-south-1"
        )
    else:
        file_path = os.path.join(UPLOAD_FOLDER_PATH, file.filename)
        fs = fsspec.filesystem('file')

        print(f"Saving file to: {file_path}")
        with fs.open(file_path, "wb") as f:
            f.write(contents)

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_id_raw = f"{file.filename}_{current_datetime}"
    file_id = hashlib.sha256(file_id_raw.encode()).hexdigest()

    return {
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "upload_time": current_datetime,
        "file_path": file_path
    }
