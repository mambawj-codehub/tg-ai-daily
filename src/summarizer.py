import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def build_summary_prompt(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Build the OpenAI prompt for Chinese daily digest generation."""
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


def generate_summary(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Generate a Chinese daily digest using OpenAI API."""
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = build_summary_prompt(messages, date_str)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的技术日报编辑，擅长归纳总结和分类。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    return response.choices[0].message.content
