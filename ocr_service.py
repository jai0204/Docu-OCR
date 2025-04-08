from fastapi import FastAPI, UploadFile, File, HTTPException
import easyocr
import cv2
import numpy as np
import uvicorn
import re
import os
import logging
from logging.handlers import RotatingFileHandler
from aadhaar import check_if_aadhaar, process_aadhaar
from pan import check_if_pan, process_pan

# Set up logging
if not os.path.exists("logs"):
    os.makedirs("logs")
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

log_handler = RotatingFileHandler("logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=20)  # 5MB per file, keeps 3 backups
log_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

logger.info("OCR service started.")

# Initialize FastAPI app
app = FastAPI()

# ✅ Load EasyOCR once at startup
reader = easyocr.Reader(['en'])

def is_blurry(image, results, base_threshold=40, min_threshold=20, max_threshold=60):
    """Dynamically adjust blur threshold based on text size in the image."""
    blur_score = calculate_blur(image)
    text_ratio = get_text_area(image, results)

    # Adjust blur threshold: If text occupies more space, allow lower threshold
    dynamic_threshold = base_threshold - (text_ratio * 65)
    dynamic_threshold = max(min_threshold, min(dynamic_threshold, max_threshold))

    logger.info(f"Blur Score: {blur_score}, Dynamic Threshold: {dynamic_threshold}, Text Ratio: {text_ratio:.2f}")
    print(f"Blur Score: {blur_score}, Dynamic Threshold: {dynamic_threshold}, Text Ratio: {text_ratio:.2f}")

    return blur_score < dynamic_threshold

def calculate_blur(image):
    """Detect blurriness using Laplacian variance"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance

def get_text_area(image, results):
    """Estimate the size of the text area in proportion to the image size."""
    total_area = image.shape[0] * image.shape[1]
    text_area = 0

    for (bbox, text, prob) in results:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        width = top_right[0] - top_left[0]
        height = bottom_right[1] - top_right[1]
        text_area += width * height

    return text_area / total_area  # Ratio of text to image size

def check_contrast(image):
    """Detect low contrast by checking pixel intensity range"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    min_intensity = np.min(gray)
    max_intensity = np.max(gray)
    contrast = max_intensity - min_intensity
    return contrast

def extract_text_from_image(results):
    return " ".join([res[1] for res in results if res[2] >= 0.41])

def extract_results_from_image(image):
    """Extract text using EasyOCR"""
    results = reader.readtext(image)
    logger.info(f"Extracted {len(results)} text regions:")
    print("\n🔍 Extracted Text:")
    for bbox, text, prob in results:
        logger.info(f"Text: {text} (Confidence: {prob:.2f})")
        print(f"{text} (Confidence: {prob:.2f})")
    return results   

def classify_document(results):
    """Check if the text contains Aadhaar or PAN"""
    if check_if_aadhaar(results):
        return "aadhaar"
    elif check_if_pan(results):
        return "pan"
    return "unknown"

@app.post("/process_ocr/")
async def process_ocr(file: UploadFile = File(...)):
    # ✅ File type restriction
    if file.content_type not in ["image/jpeg", "image/png"]:
        logger.error(f"Invalid file type: {file.filename} - {file.content_type}")
        raise HTTPException(status_code=400, detail="Only JPEG and PNG files are allowed")

    # ✅ File size restriction (5MB)
    if file.size > 5 * 1024 * 1024:
        logger.error(f"File size too large: {file.filename} - {file.size} bytes")
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")

    file_bytes = await file.read()

    # Convert to OpenCV format
    image = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)

    logger.info(f"Received file: {file.filename}, Size: {file.size} bytes, Type: {file.content_type}")

    # Extract results using EasyOCR
    results = extract_results_from_image(image)

    # ✅ Step 1: Check for blurriness
    if is_blurry(image, results):  # Adjust threshold as needed
        return {"error": "Image is too blurry for OCR processing."}

    # ✅ Step 2: Check for low contrast
    contrast_score = check_contrast(image)
    if contrast_score < 40:  # Adjust threshold as needed
        logger.warning("Low contrast detected.")
        return {"error": "Image contrast is too low for OCR processing."}

    # Classify document type
    doc_type = classify_document(results)
    logger.info(f"Document Type: {doc_type}")

    if doc_type == "unknown":
        return {"error": "No Aadhaar or PAN detected"}
    elif doc_type == "aadhaar":
        return process_aadhaar(results)
    elif doc_type == "pan":
        return process_pan(results)
    else:
        return None