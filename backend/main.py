from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import os
import shutil
from gauge_reader import read_gauge_pressure

app = FastAPI()

# Allow your React frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This is the crucial line for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the YOLOv8 model
# If you haven't finished training, you can temporarily use 'yolov8n.pt' to test the endpoint
MODEL_PATH = "../models/gauge_yolov8_best.pt" 
try:
    model = YOLO(MODEL_PATH)
except:
    print(f"Warning: Custom model not found at {MODEL_PATH}. Loading base YOLOv8n for testing.")
    model = YOLO("yolov8n.pt")

TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/predict")
async def predict_pressure(
    file: UploadFile = File(...),
    min_val: float = Form(-1.0), # Accepts dynamic min
    max_val: float = Form(1.5)   # Accepts dynamic max
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    file_path = os.path.join(TEMP_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Pass the dynamic values to your OpenCV script
        reading = read_gauge_pressure(file_path, min_val=min_val, max_val=max_val)

        os.remove(file_path)
        return reading

    except Exception as e:
        return {"error": str(e)}

# To run the server locally:
# uvicorn main:app --reload