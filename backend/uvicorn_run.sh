#!/usr/bin/env bash
uvicorn ocr_service.main:app --host 0.0.0.0 --port 8000 --reload