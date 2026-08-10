import json
import os
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str) -> Dict[str, Any]:
    file_path = DATA_DIR / filename

    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(filename: str, data: Dict[str, Any]) -> None:
    file_path = DATA_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def clean_json_response(text: str) -> Dict[str, Any]:
    """
    Converts an AI JSON response into a Python dictionary.
    Also handles responses wrapped in ```json ... ```.
    """

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])

        raise ValueError("AI returned invalid JSON")


def average(values):
    if not values:
        return 0

    return round(sum(values) / len(values), 2)