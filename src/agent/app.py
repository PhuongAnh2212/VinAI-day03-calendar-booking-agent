import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Allow imports from src/agent and src/telemetry
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_model_react import run_agent_message  # noqa: E402
from telemetry.logger import logger  # noqa: E402

app = FastAPI(title="Calendar Booking Agent API")


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    reply: str


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required.")

    try:
        reply = run_agent_message(req.message, history=req.history)
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.log_event("API_ERROR", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3001)
