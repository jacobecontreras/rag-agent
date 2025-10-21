import time
import threading
import json
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from services.agent_service import agent_service
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from database.database import init_database, insert_report_metadata
from utils.processing_utils import validate_leapp_directory, process_leapp_report

load_dotenv()
app = FastAPI()

init_database()

class UploadRequest(BaseModel):
    directory_path: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    job_name: Optional[str] = None

@app.post("/upload")
async def upload_report(request: UploadRequest):
    if not validate_leapp_directory(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid LEAPP report directory: No TSV, KML or Timeline directory found")

    job_name = f"report_{int(time.time())}"
    insert_report_metadata(job_name, request.directory_path)

    # Start background processing
    threading.Thread(target=process_leapp_report, args=(job_name, request.directory_path)).start()
    return {"success": True, "job_name": job_name}


@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with AI assistant for forensic analysis - real-time streaming"""
    async def stream_response():
        try:
            async for response_chunk in agent_service.process_agent_message(request.message, request.session_id, request.job_name):
                # Pass through the structured JSON from agent service
                yield f"data: {response_chunk}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            # Send error message
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


@app.get("/")
async def root():
    return {"message": "LEAPP Forensic Agent API"}
