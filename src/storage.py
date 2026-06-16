import json
import os
from typing import List, Dict, Any


def save_raw_messages(messages: List[Dict[str, Any]], date_str: str, base_dir: str = "data/raw") -> str:
    """Save raw messages to a date-named JSON file."""
    os.makedirs(base_dir, exist_ok=True)
    filename = f"tg_raw_{date_str}.json"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    return filepath


def save_summary(content: str, date_str: str, base_dir: str = "data/summaries") -> str:
    """Save summary Markdown to a date-named file."""
    os.makedirs(base_dir, exist_ok=True)
    filename = f"tg_summary_{date_str}.md"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
