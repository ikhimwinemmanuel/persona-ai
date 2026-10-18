# Python's unittest.mock library to simulate Amazon S3 to test our code without creating a bucket, using AWS credentials or incurring charges.



import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import server


def test_s3_storage():
    session_id = "test-session-123"
    messages = [
        {"role": "user", "content": "Hello PersonaAI"}
    ]

    fake_s3 = MagicMock()

    fake_s3.get_object.return_value = {
        "Body": BytesIO(json.dumps(messages).encode("utf-8"))
    }

    with (
        patch.object(server, "USE_S3", True),
        patch.object(server, "S3_BUCKET", "test-personaai-bucket"),
        patch.object(server, "s3", fake_s3),
    ):
        server.save_conversation(session_id, messages)
        loaded = server.load_conversation(session_id)

    assert loaded == messages
    fake_s3.put_object.assert_called_once()
    fake_s3.get_object.assert_called_once_with(
        Bucket="test-personaai-bucket",
        Key="sessions/test-session-123.json"
    )

    print("S3 STORAGE TEST PASSED")


if __name__ == "__main__":
    test_s3_storage()
