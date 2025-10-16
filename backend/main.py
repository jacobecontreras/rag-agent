import os
import time
import threading
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from database.database import init_database, insert_report_metadata
from utils.processing_utils import validate_leapp_directory, process_leapp_report
from services.ai_service import ai_service
from logs.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

init_database()
logger.info("LEAPP Forensic Agent API started")

class UploadRequest(BaseModel):
    directory_path: str

class ChatRequest(BaseModel):
    message: str

@app.post("/upload")
async def upload_report(request: UploadRequest):
    logger.info(f"Upload request received for directory: {request.directory_path}")

    if not validate_leapp_directory(request.directory_path):
        logger.warning(f"Invalid LEAPP directory: {request.directory_path}")
        raise HTTPException(status_code=400, detail="Invalid LEAPP report directory: No TSV, KML or Timeline directory found")

    job_name = f"report_{int(time.time())}"
    insert_report_metadata(job_name, request.directory_path)

    logger.info(f"Created job {job_name} for directory: {request.directory_path}")

    # Start background processing
    threading.Thread(target=process_leapp_report, args=(job_name, request.directory_path)).start()
    logger.info(f"Started background processing for job: {job_name}")

    return {"success": True, "job_name": job_name}


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages with AI service"""
    logger.info(f"Chat request received: {request.message[:100]}...")

    try:
        ai_response = await ai_service.send_message(request.message)
        logger.info("Chat response generated successfully")
        return {"response": ai_response}

    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "LEAPP Forensic Agent API"}
