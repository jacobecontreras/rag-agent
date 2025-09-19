import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        stream = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "LEAPP Forensic Agent",
            },
            model="z-ai/glm-4.5",
            messages=[
                {
                    "role": "user",
                    "content": request.message
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

@app.get("/")
async def root():
    return {"message": "LEAPP Forensic Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)