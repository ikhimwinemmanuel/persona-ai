
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List, Dict
from pathlib import Path
from botocore.exceptions import ClientError
from context import prompt
import boto3
import json
import os
import uuid


# Load environment variables
load_dotenv(override=True)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Amazon Bedrock configuration
BEDROCK_REGION = os.getenv("DEFAULT_AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "global.amazon.nova-2-lite-v1:0"
)

bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION
)

# Conversation storage configuration
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET")

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"

if not USE_S3:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

s3 = boto3.client("s3") if USE_S3 else None


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


# Amazon Bedrock inference
def call_bedrock(conversation: List[Dict], user_message: str) -> str:
    """Generate an AI response using Amazon Bedrock Converse API."""

    messages = []

    # Include recent conversation history
    for msg in conversation[-50:]:
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })

    # Add the current user message
    messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })

    try:
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": prompt()}],
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        )

        return "".join(
            block.get("text", "")
            for block in response["output"]["message"]["content"]
        )

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        print(f"Bedrock invocation failed: {error_code}")

        if error_code == "AccessDeniedException":
            raise HTTPException(
                status_code=403,
                detail="Access denied to the Bedrock model"
            )

        if error_code == "ValidationException":
            raise HTTPException(
                status_code=400,
                detail="Invalid request to the Bedrock model"
            )

        raise HTTPException(
            status_code=502,
            detail="Bedrock model invocation failed"
        )


# Request / Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {
        "message": "PersonaAI API",
        "ai_model": BEDROCK_MODEL_ID
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "use_s3": USE_S3,
        "bedrock_model": BEDROCK_MODEL_ID
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        # Retrieve conversation history
        conversation = load_conversation(session_id)

        # Generate a response using Amazon Bedrock
        assistant_response = call_bedrock(
            conversation,
            request.message
        )

        # Update conversation history
        conversation.append({
            "role": "user",
            "content": request.message
        })
        conversation.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Persist conversation
        save_conversation(session_id, conversation)

        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as error:
        print(f"Chat endpoint error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process chat request"
        )


@app.get("/sessions")
async def list_sessions():
    """List locally stored conversation sessions."""
    sessions = []

    if USE_S3:
        raise HTTPException(
            status_code=501,
            detail="Session listing is not available for S3 storage"
        )

    for file_path in MEMORY_DIR.glob("*.json"):
        session_id = file_path.stem

        with open(file_path, "r", encoding="utf-8") as file:
            conversation = json.load(file)

        sessions.append({
            "session_id": session_id,
            "message_count": len(conversation),
            "last_message": (
                conversation[-1]["content"] if conversation else None
            )
        })

    return {"sessions": sessions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
