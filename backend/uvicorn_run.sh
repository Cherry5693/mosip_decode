#!/bin/bash
cd /workspaces/mosip_decode/backend/ocr_service
uvicorn main:app --reload --host 0.0.0.0 --port 8000