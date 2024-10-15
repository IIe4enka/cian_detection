from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
from pydantic import BaseModel
from ultralytics import YOLO
import time
from PIL import Image, UnidentifiedImageError
from src.utils import download_image

# Load the trained model
model = YOLO('src/models/yolov8n-cian.pt')
app = FastAPI()


def predict_image(image):
    try:
        start_time = time.time()
        results = model.predict(source=image, save=False, save_txt=False)
        for result in results:
            probs = result.probs.data
            plan_prob = probs[1].item()
            no_plan_prob = probs[0].item()
            prediction = True if plan_prob > no_plan_prob else False
        predict_time = time.time() - start_time
        return {
            "prediction": prediction,
            "plan_probability": plan_prob,
            "predict_time": predict_time,
            "error": None
        }
    except Exception as e:
        return {
            "prediction": None,
            "plan_probability": None,
            "predict_time": None,
            "error": str(e)
        }

class UrlInput(BaseModel):
    image_urls: list[str]


@app.post("/detect_plans_from_urls/")
async def detect_plans_from_urls(input: UrlInput):
    image_urls = input.image_urls
    images_and_times = []
    total_download_time = 0
    results = []
    
    # Download images, handling errors
    for url in image_urls:
        try:
            image, download_time = download_image(url)
            images_and_times.append((image, download_time))
            total_download_time += download_time
        except Exception as e:
            results.append({
                "url": url,
                "error": f"Failed to download image: {str(e)}",
                "prediction": None,
                "plan_probability": None,
                "predict_time": None
            })
    
    images = [image for image, _ in images_and_times]
    total_predict_time = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(predict_image, image) for image in images]
        
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            result["url"] = image_urls[i]  # Include the URL in the result
            results.append(result)
            if result["predict_time"] is not None:
                total_predict_time += result['predict_time']

    return JSONResponse(content={
        "images": results,
        "total_download_time": total_download_time,
        "total_predict_time": total_predict_time,
    })


@app.post("/detect_plans_from_files/")
async def detect_plans_from_files(files: list[UploadFile] = File(...)):
    images = []
    results = []
    total_predict_time = 0
    
    # Handle file reading errors
    for file in files:
        try:
            image = Image.open(BytesIO(await file.read()))
            images.append(image)
        except UnidentifiedImageError:
            results.append({
                "file_name": file.filename,
                "error": "Unrecognized image file"
            })
        except Exception as e:
            results.append({
                "file_name": file.filename,
                "error": f"Failed to read image file: {str(e)}"
            })

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(predict_image, image) for image in images]
        
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            result["file_name"] = files[i].filename  # Include the file name in the result
            results.append(result)
            if result["predict_time"] is not None:
                total_predict_time += result['predict_time']

    return JSONResponse(content={
        "images": results,
        "total_predict_time": total_predict_time,
    })




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
