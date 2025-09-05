import fitz
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Union

def pil_to_cv(img: Image.Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def load_doc_as_images(path: Union[str, Path], dpi: int = 220) -> List[np.ndarray]:
    path = str(path)
    if any(path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]):
        img = Image.open(path).convert("RGB")
        return [pil_to_cv(img)]
    doc = fitz.open(path)
    pages = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for page in doc:
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(pil_to_cv(img))
    return pages