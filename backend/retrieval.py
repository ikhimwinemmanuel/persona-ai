
from resources import load_facts, load_summary, load_resume
import json


def load_documents() -> list[dict]:
    """Load professional knowledge into searchable documents."""

    return [
        {
            "source": "facts.json",
            "text": json.dumps(load_facts(), ensure_ascii=False),
        },
        {
            "source": "summary.txt",
            "text": load_summary(),
        },
        {
            "source": "Emmanuel_Resume.pdf",
            "text": load_resume(),
        },
    ]
