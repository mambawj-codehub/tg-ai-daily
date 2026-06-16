import json
import os
import tempfile
from src.storage import save_raw_messages, save_summary


def test_save_raw_messages():
    messages = [
        {"msg_id": 1, "channel": "@test", "label": "测试", "date": "2026-06-08T12:00:00", "text": "hello", "link": "https://t.me/test/1", "content_hash": "abc"},
        {"msg_id": 2, "channel": "@test", "label": "测试", "date": "2026-06-08T13:00:00", "text": "world", "link": "https://t.me/test/2", "content_hash": "def"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = save_raw_messages(messages, date_str="2026-06-08", base_dir=tmpdir)
        assert os.path.exists(filepath)
        assert filepath.endswith("tg_raw_2026-06-08.json")

        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert len(loaded) == 2
        assert loaded[0]["msg_id"] == 1
        assert loaded[1]["text"] == "world"


def test_save_summary():
    summary_md = "# TG 日报 — 2026-06-08\n\n## AI 技术\n测试内容"
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = save_summary(summary_md, date_str="2026-06-08", base_dir=tmpdir)
        assert os.path.exists(filepath)
        assert filepath.endswith("tg_summary_2026-06-08.md")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "TG 日报" in content
