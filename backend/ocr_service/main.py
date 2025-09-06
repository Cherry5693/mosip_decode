from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from pathlib import Path
import tempfile, shutil, json

from ocr.pdf_utils import load_doc_as_images
from ocr.preprocess import preprocess_for_ocr
from ocr.quality import compute_quality_metrics
from ocr.detect import Detector
from ocr.trocr_recognizer import TrOCRRecognizer
from ocr.tesseract_recognizer import TessRecognizer
from ocr.field_mapping import FieldMapper, load_templates
from ocr.verify import verify_fields, overall_cer

app = FastAPI(title="Local OCR Extract + Verify")

# ✅ Fix CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector()
trocr_print = TrOCRRecognizer(model_id="microsoft/trocr-small-printed")
trocr_hand = TrOCRRecognizer(model_id="microsoft/trocr-small-handwritten")
tess = TessRecognizer()
templates = load_templates(Path(__file__).parent / "models" / "templates")

# Serve frontend files (optional if you open index.html directly)
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
async def root_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"status": "running"})


@app.post("/api/ocr/extract")
async def extract_api(
    file: UploadFile = File(...),
    docType: str = Form("generic"),
    language: str = Form("eng"),
    use_handwriting: bool = Form(False),
    prefer_trocr: bool = Form(True),
) -> Any:
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file provided")
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td) / file.filename
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        pages = load_doc_as_images(tmp_path)
        all_tokens, all_quality, all_page_w_h = [], [], []
        for pi, page_img in enumerate(pages, start=1):
            proc = preprocess_for_ocr(page_img)
            q = compute_quality_metrics(proc)
            tokens = detector.recognize(proc, lang="ar" if language.lower().startswith("ar") else "en")
            all_tokens.append({"page": pi, "tokens": tokens})
            all_quality.append({"page": pi, **q})
            h, w = proc.shape[:2]
            all_page_w_h.append({"page": pi, "w": w, "h": h})

        mapper = FieldMapper(templates.get(docType, {}), lang=language)
        fields = mapper.extract_fields(all_tokens)

        if prefer_trocr and language.lower().startswith("en"):
            for fld in fields:
                if "bbox" in fld and fld["bbox"]:
                    page_idx = fld["page"] - 1
                    x1, y1, x2, y2 = map(int, fld["bbox"])
                    crop = pages[page_idx][y1:y2, x1:x2]
                    model = trocr_hand if use_handwriting else trocr_print
                    txt, conf = model.recognize(crop)
                    if txt:
                        fld["value"] = txt
                        fld["confidence"] = max(fld.get("confidence", 0.0), conf)

        resp = {
            "documentId": file.filename,
            "language": language,
            "pages": len(pages),
            "fields": fields,
            "quality": {
                "perPage": all_quality,
                "avgBlur": sum(p["blur"] for p in all_quality) / len(all_quality),
                "avgBrightness": sum(p["brightness"] for p in all_quality) / len(all_quality),
            },
            "pageSize": all_page_w_h,
        }
        return JSONResponse(resp)


@app.post("/api/ocr/verify")
async def verify_api(
    file: UploadFile = File(...),
    submittedFields: str = Form(...),
    docType: str = Form("generic"),
    language: str = Form("eng"),
    prefer_trocr: bool = Form(True),
) -> Any:
    try:
        client_fields = json.loads(submittedFields)
        assert isinstance(client_fields, list)
    except Exception:
        raise HTTPException(status_code=400, detail="submittedFields must be JSON list")

    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td) / file.filename
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        pages = load_doc_as_images(tmp_path)
        all_tokens = []
        for pi, page_img in enumerate(pages, start=1):
            proc = preprocess_for_ocr(page_img)
            tokens = detector.recognize(proc, lang="ar" if language.lower().startswith("ar") else "en")
            all_tokens.append({"page": pi, "tokens": tokens})
        mapper = FieldMapper(templates.get(docType, {}), lang=language)
        observed_fields = mapper.extract_fields(all_tokens)

    results, passfail = verify_fields(client_fields, observed_fields)
    overall = {"passed": passfail, "cer": overall_cer(client_fields, observed_fields)}
    return JSONResponse({"documentId": file.filename, "results": results, "overall": overall})
