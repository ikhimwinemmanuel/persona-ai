
import json
from pathlib import Path

from pypdf import PdfReader


DATA_DIR = Path(__file__).resolve().parent / "data"


def load_facts():
    with open(DATA_DIR / "facts.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_summary():
    return (DATA_DIR / "summary.txt").read_text(encoding="utf-8")


def load_style():
    return (DATA_DIR / "style.txt").read_text(encoding="utf-8")


def load_resume():
    reader = PdfReader(DATA_DIR / "Emmanuel_Resume.pdf")
    return "\n".join(page.extract_text() or "" for page in reader.pages)
