from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from io import BytesIO
from ultralytics import YOLO
import psycopg2
import time
from PIL import Image

from src.utils import download_image

db_router = APIRouter()

def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

def get_unprocessed_images(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM images WHERE is_processed = FALSE")
    rows = cursor.fetchall()
    cursor.close()
    return rows

def mark_image_as_processed(conn, image_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET is_processed = TRUE WHERE id = %s", (image_id,))
    conn.commit()
    cursor.close()

def insert_plan_image(conn, image_url):
    start_time = time.time()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO plans (url) VALUES (%s)", (image_url,))
    conn.commit()
    cursor.close()
    insert_time = time.time() - start_time
    return insert_time

def process_image(image_id, image, image_url conn):
    try:
        if image is None:
            image, download_time = download_image(image_url)
        else:
            download_time = 0
        prediction, plan_prob, predict_time = predict_image(image)
        insert_time = 0
        if prediction == 'Plan':
            insert_time = insert_plan_image(conn, image_url)

        mark_image_as_processed(conn, image_id)

        return {
            "url": image_url,
            "plan_probability": plan_prob,
            "download_time": download_time,
            "predict_time": predict_time,
            "insert_time": insert_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image from {image_url}: {e}")
    


@app.post("/detect_plans/")
async def detect_plans():
    conn = connect_to_db()
    unprocessed_images = get_unprocessed_images(conn)

    plan_images = []
    total_download_time = 0
    total_predict_time = 0
    total_insert_time = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_image, image_id, image_url, conn) for image_id, image_url in unprocessed_images]
        
        for future in as_completed(futures):
            result = future.result()
            plan_images.append(result)
            total_download_time += result['download_time']
            total_predict_time += result['predict_time']
            total_insert_time += result['insert_time']

    conn.close()
    return JSONResponse(content={
        "plan_images": plan_images,
        "total_download_time": total_download_time,
        "total_predict_time": total_predict_time,
        "total_insert_time": total_insert_time
    })

