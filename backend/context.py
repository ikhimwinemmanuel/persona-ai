
import json
from datetime import datetime, timezone

from resources import (
    load_facts,
    load_summary,
    load_style,
    load_resume,
)


def prompt():
    facts = load_facts()
    summary = load_summary()
    style = load_style()
    resume = load_resume()

    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""
You are PersonaAI, an AI assistant representing Ikhimwin Emmanuel.

Current date (UTC): {current_date}

COMMUNICATION GUIDELINES:
{style}

PROFESSIONAL FACTS:
{json.dumps(facts, indent=2, ensure_ascii=False)}

PROFESSIONAL SUMMARY:
{summary}

RESUME:
{resume}

Use the information above to answer questions about Emmanuel.
Do not invent information that is not provided.
"""
