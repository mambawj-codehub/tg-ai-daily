import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = "你是一个专业的技术日报编辑，擅长归纳总结和分类。"


def build_summary_prompt(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Build the prompt for Chinese daily digest generation."""
    messages_text = ""
    for i, msg in enumerate(messages, 1):
        messages_text += f"{i}. [{msg['label']}] {msg['text']}\n   链接: {msg['link']}\n\n"

    prompt = f"""你是一个技术日报编辑。以下是 {date_str} 从多个 Telegram 频道收集的消息。

请按以下要求生成中文日报：

1. 按主题/领域将消息分类（如：AI 技术、行业新闻、工具推荐、观点讨论等）
2. 过滤掉纯广告和推广内容
3. 每个分类下写 2-3 句综述，概括该类消息的核心内容
4. 每条消息要点后附上来源标签和原文链接（格式：来源：[频道标签](链接)）
5. 使用 Markdown 格式输出

=== 消息列表 ===

{messages_text}
"""
    return prompt


def _generate_openai(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Generate summary using OpenAI API."""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = build_summary_prompt(messages, date_str)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
    )
    return response.choices[0].message.content


def _generate_gemini(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Generate summary using Google Gemini API."""
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 未设置，请在 .env 中配置")

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = build_summary_prompt(messages, date_str)

    response = client.models.generate_content(
        model=model,
        contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
    )
    return response.text


def generate_summary(messages: List[Dict[str, Any]], date_str: str, provider: str = "openai") -> str:
    """Generate a Chinese daily digest.

    Args:
        messages: List of message dicts
        date_str: Date string for the report title
        provider: "openai" or "gemini"
    """
    if provider == "gemini":
        return _generate_gemini(messages, date_str)
    else:
        return _generate_openai(messages, date_str)
