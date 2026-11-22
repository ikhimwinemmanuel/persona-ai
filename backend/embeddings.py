
import json

import boto3


MODEL_ID = "amazon.titan-embed-text-v2:0"
DIMENSIONS = 512


def embed_text(text: str, client=None) -> list[float]:
    """Generate a normalized embedding using Amazon Titan V2."""

    if not text.strip():
        raise ValueError("Text cannot be empty")

    if client is None:
        client = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
        )

    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": text,
            "dimensions": DIMENSIONS,
            "normalize": True,
        }),
    )

    result = json.loads(response["body"].read())
    embedding = result["embedding"]

    if len(embedding) != DIMENSIONS:
        raise ValueError("Unexpected embedding dimensions")

    return embedding
