from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO
from ultralytics import YOLO
import time
from PIL import Image
from src.utils import download_image

# Load the trained model
model = YOLO('runs/classify/train/weights/best.pt')
app = FastAPI()


def predict_image(image):
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
        "predict_time": predict_time
    }


@app.post("/detect_plans_from_urls/")
async def detect_plans_from_urls(image_urls: list[str]):
    images_and_times = [download_image(image_url) for image_url in image_urls]
    images = [image for image, _ in images_and_times]
    total_download_time = sum(download_time for _, download_time in images_and_times)
    total_predict_time = 0
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(predict_image, image) for image in images]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            total_predict_time += result['predict_time']

    return JSONResponse(content={
        "images": results,
        "total_download_time": total_download_time,
        "total_predict_time": total_predict_time,
    })


@app.post("/detect_plans_from_files/")
async def detect_plans_from_files(files: list[UploadFile] = File(...)):
    images = [Image.open(BytesIO(await file.read())) for file in files]
    total_predict_time = 0
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(predict_image, image) for image in images]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            total_predict_time += result['predict_time']

    return JSONResponse(content={
        "images": results,
        "total_predict_time": total_predict_time,
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)