# OCR Extraction + Verification (Offline, FastAPI)

Two APIs:
- /api/ocr/extract: OCR extraction with fields, confidences, bboxes, quality scores.
- /api/ocr/verify: submitted data vs. extracted values with per-field status and combined score.

Stacks: FastAPI, PaddleOCR (det/rec), TrOCR (English printed/handwritten), OpenCV, PyMuPDF, RapidFuzz.