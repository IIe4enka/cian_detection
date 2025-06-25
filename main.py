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
model = YOLO('src/models/best_22_10_2024.pt')
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
    successful_urls = []  # Track URLs for successfully downloaded images
    
    # Download images, handling errors
    for url in image_urls:
        try:
            image, download_time = download_image(url)
            images_and_times.append((image, download_time))
            successful_urls.append(url)  # Track the URL for this successful download
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
        # Create a mapping between futures and their corresponding URLs
        future_to_url = {executor.submit(predict_image, image): url 
                        for image, url in zip(images, successful_urls)}
        
        for future in as_completed(future_to_url):
            result = future.result()
            result["url"] = future_to_url[future]  # Get the correct URL for this future
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
    successful_files = []  # Track filenames for successfully loaded images
    
    # Handle file reading errors
    for file in files:
        try:
            image = Image.open(BytesIO(await file.read()))
            images.append(image)
            successful_files.append(file.filename)  # Track the filename for this successful load
        except UnidentifiedImageError:
            results.append({
                "file_name": file.filename,
                "error": "Unrecognized image file",
                "prediction": None,
                "plan_probability": None,
                "predict_time": None
            })
        except Exception as e:
            results.append({
                "file_name": file.filename,
                "error": f"Failed to read image file: {str(e)}",
                "prediction": None,
                "plan_probability": None,
                "predict_time": None
            })

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a mapping between futures and their corresponding filenames
        future_to_filename = {executor.submit(predict_image, image): filename 
                             for image, filename in zip(images, successful_files)}
        
        for future in as_completed(future_to_filename):
            result = future.result()
            result["file_name"] = future_to_filename[future]  # Get the correct filename for this future
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
