import cv2
import numpy as np

def variance_of_laplacian(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def avg_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray) / 255.0)

def compute_quality_metrics(img):
    blur = variance_of_laplacian(img)
    brightness = avg_brightness(img)
    return {"blur": blur, "brightness": brightness}