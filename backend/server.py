from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
import json
import uuid
from datetime import datetime
from pathlib import Path
from context import prompt
import boto3 #AWS sdk for python
from botocore.exceptions import ClientError # Error handling for AWS S3





# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI()

# Conversation storage configuration
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET")

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"

if not USE_S3:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

s3 = boto3.client("s3") if USE_S3 else None


# Load personality details
def load_personality():
    with open("me.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


PERSONALITY = load_personality()


# Memory functions

def load_conversation(session_id: str) -> List[Dict]:
    """Load conversation history from local storage or S3."""

    if USE_S3:
        if not S3_BUCKET:
            raise RuntimeError("S3_BUCKET is not configured")

        object_key = f"sessions/{session_id}.json"

        try:
            response = s3.get_object(
                Bucket=S3_BUCKET,
                Key=object_key
            )

            content = response["Body"].read().decode("utf-8")
            return json.loads(content)

        except ClientError as error:
            error_code = error.response["Error"]["Code"]

            if error_code in ("NoSuchKey", "404"):
                return []

            raise

    file_path = MEMORY_DIR / f"{session_id}.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    return []




def save_conversation(session_id: str, messages: List[Dict]):
    """Save conversation history to local storage or S3."""

    if USE_S3:
        if not S3_BUCKET:
            raise RuntimeError("S3_BUCKET is not configured")

        object_key = f"sessions/{session_id}.json"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=object_key,
            Body=json.dumps(messages, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json"
        )

        return

    file_path = MEMORY_DIR / f"{session_id}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=2, ensure_ascii=False)



# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "PersonaAI API with Memory"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Load conversation history
        conversation = load_conversation(session_id)

        # Build messages with history
        messages = [{"role": "system", "content": prompt()}]

        # Add conversation history
        for msg in conversation:
            messages.append(msg)

        # Add current message
        messages.append({"role": "user", "content": request.message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        assistant_response = response.choices[0].message.content

        # Update conversation history
        conversation.append({"role": "user", "content": request.message})
        conversation.append({"role": "assistant", "content": assistant_response})

        # Save updated conversation
        save_conversation(session_id, conversation)

        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions():
    """List all conversation sessions"""
    sessions = []
    for file_path in MEMORY_DIR.glob("*.json"):
        session_id = file_path.stem
        with open(file_path, "r", encoding="utf-8") as f:
            conversation = json.load(f)
            sessions.append({
                "session_id": session_id,
                "message_count": len(conversation),
                "last_message": conversation[-1]["content"] if conversation else None
            })
    return {"sessions": sessions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
