from io import BytesIO
import time
from PIL import Image

from fastapi import HTTPException
import requests


def download_image(url):
    start_time = time.time()
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to download image from {url}")
    image = Image.open(BytesIO(response.content))
    download_time = time.time() - start_time
    return image, download_time