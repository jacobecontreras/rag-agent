import os
import subprocess
import time
import threading
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import json
from database.database import init_database, get_db_connection, insert_report_metadata
from utils.processing_utils import validate_leapp_directory, process_leapp_report

load_dotenv()
app = FastAPI()


init_database()

# Models

class ChatRequest(BaseModel):
    message: str

class DirectorySelectRequest(BaseModel):
    pass

class UploadRequest(BaseModel):
    directory_path: str


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# API Endpoints


@app.get("/chat")
async def chat(message: str):
    try:
        stream = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "LEAPP Forensic Agent",
            },
            model="z-ai/glm-4.5",
            messages=[
                {
                    # SYSTEM PROMPT
                    "role": "system",
                    "content": "You are a LEAPP forensic analysis assistant. You specialize in analyzing aLEAPP and iLEAPP reports. Help users analyze forensic data and answer questions about their LEAPP reports."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            stream=True
        )

        def generate_tokens():
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(generate_tokens(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/upload")
async def upload_report(request: UploadRequest):
    """Upload and process LEAPP report"""
    try:
        if not validate_leapp_directory(request.directory_path):
            raise HTTPException(status_code=400, detail="Invalid LEAPP report directory: No TSV, KML or Timeline directory found")

        job_name = f"report_{int(time.time())}"
        insert_report_metadata(job_name, request.directory_path)

        # Start background processing
        threading.Thread(target=process_leapp_report,
                        args=(job_name, request.directory_path)).start()

        return {"success": True, "job_name": job_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_name}")
async def get_status(job_name: str):
    """Get processing status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, error_message FROM reports WHERE job_name = ?", (job_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"job_name": job_name, "status": result[0], "error_message": result[1]}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/")
async def root():
    return {"message": "LEAPP Forensic Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
