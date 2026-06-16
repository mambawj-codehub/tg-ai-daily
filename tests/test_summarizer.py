from src.summarizer import build_summary_prompt


def test_build_summary_prompt():
    messages = [
        {"msg_id": 1, "channel": "@test", "label": "测试频道", "text": "GPT-5 released today", "link": "https://t.me/test/1"},
        {"msg_id": 2, "channel": "@test2", "label": "科技新闻", "text": "New AI chip announced", "link": "https://t.me/test2/2"},
    ]
    date_str = "2026-06-08"
    prompt = build_summary_prompt(messages, date_str)
    assert "2026-06-08" in prompt
    assert "GPT-5" in prompt
    assert "测试频道" in prompt
    assert "主题" in prompt
    assert "分类" in prompt
    assert "Markdown" in prompt
    assert len(prompt) > 100
