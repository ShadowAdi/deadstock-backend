import os
import requests
from fastapi import UploadFile, HTTPException, status
from typing import List
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()

UPLOADTHING_API_KEY = os.getenv("UPLOADTHING_KEY")
UPLOADTHING_API_URL = "https://api.uploadthing.com/v6/uploadFiles"

async def upload_files(files: List[UploadFile]) -> List[str]:
    if not UPLOADTHING_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="UploadThing API key is not configured."
        )

    if len(files) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can upload a maximum of 4 images."
        )

    uploaded_urls = []
    headers = {
        "x-uploadthing-api-key": UPLOADTHING_API_KEY,
        "x-uploadthing-version": "6.4.0"
    }

    for file in files:
        try:
            files_to_upload = [('files', (file.filename, await file.read(), file.content_type))]
            response = requests.post(UPLOADTHING_API_URL, headers=headers, files=files_to_upload)
            response.raise_for_status()
            uploaded_urls.append(response.json()["data"]["url"])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file to UploadThing: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during file upload: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during file upload."
            )

    return uploaded_urls
