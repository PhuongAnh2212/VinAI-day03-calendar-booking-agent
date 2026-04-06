import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# --- Config ---
PORT = int(os.getenv("PORT", 3001))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# --- App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request schema ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

# --- Routes ---
@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="message is required")

    messages = [
        {
            "role": "system",
            "content": "You are a calendar booking assistant. Ask for missing details like time, duration, timezone, and attendees. Keep responses concise and helpful.",
        },
        *([m.dict() for m in req.history] if req.history else []),
        {"role": "user", "content": req.message},
    ]

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "ollama request failed",
                    "details": response.text,
                },
            )

        data = response.json()
        reply = data.get("message", {}).get("content", "")

        return {"reply": reply}

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "server error", "details": str(e)},
        )

# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)