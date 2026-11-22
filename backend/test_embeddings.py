
import json
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from embeddings import embed_text, DIMENSIONS


def test_embed_text():
    fake_client = MagicMock()

    fake_client.invoke_model.return_value = {
        "body": BytesIO(
            json.dumps({
                "embedding": [0.0] * DIMENSIONS
            }).encode()
        )
    }

    result = embed_text("Emmanuel knows Python", fake_client)

    assert len(result) == DIMENSIONS

    fake_client.invoke_model.assert_called_once()


def test_embed_empty_text():
    with pytest.raises(ValueError):
        embed_text("   ")
