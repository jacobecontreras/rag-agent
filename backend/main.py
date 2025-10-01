import os
import time
import threading
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from database.database import init_database, insert_report_metadata
from utils.processing_utils import validate_leapp_directory, process_leapp_report

load_dotenv()
app = FastAPI()

init_database()

class UploadRequest(BaseModel):
    directory_path: str

@app.post("/upload")
async def upload_report(request: UploadRequest):
    if not validate_leapp_directory(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid LEAPP report directory: No TSV, KML or Timeline directory found")

    job_name = f"report_{int(time.time())}"
    insert_report_metadata(job_name, request.directory_path)

    # Start background processing
    threading.Thread(target=process_leapp_report, args=(job_name, request.directory_path)).start()
    return {"success": True, "job_name": job_name}


@app.get("/")
async def root():
    return {"message": "LEAPP Forensic Agent API"}
