# tg-ai-daily 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Python CLI 工具，拉取配置的 Telegram 频道过去 24 小时消息，去重、过滤广告后，通过 OpenAI API 生成按主题分类的中文日报摘要。

**Architecture:** 模块化 CLI，`main.py` 作为单入口编排 5 个独立模块（fetcher → dedup → filter → summarizer → storage），线性流水线执行。每个模块职责单一、接口清晰、可独立测试。

**Tech Stack:** Python 3.10+, Telethon, OpenAI Python SDK, PyYAML, python-dotenv, pytest

---

### Task 1: 项目脚手架

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `config/channels.yaml`
- Create: `data/raw/.gitkeep`
- Create: `data/summaries/.gitkeep`
- Create: `src/__init__.py`

- [ ] **Step 1: 创建 .gitignore**

```bash
cat > /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/.gitignore << 'EOF'
.env
*.session
data/raw/
__pycache__/
*.pyc
EOF
```

- [ ] **Step 2: 创建 .env.example**

```bash
cat > /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/.env.example << 'EOF'
# Telegram API 凭证 (从 https://my.telegram.org 获取)
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash

# OpenAI API 配置
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
EOF
```

- [ ] **Step 3: 创建 requirements.txt**

```bash
cat > /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/requirements.txt << 'EOF'
telethon>=1.36.0
openai>=1.50.0
pyyaml>=6.0
python-dotenv>=1.0.0
EOF
```

- [ ] **Step 4: 创建 config/channels.yaml**

```bash
cat > /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/config/channels.yaml << 'EOF'
# Telegram 频道配置
# username: 频道用户名或链接
# label: 中文标签，用于摘要中展示
channels:
  # - username: "@example_channel"
  #   label: "示例频道"
EOF
```

- [ ] **Step 5: 创建数据目录和 python package 目录**

```bash
mkdir -p /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/data/raw
mkdir -p /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/data/summaries
touch /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/data/raw/.gitkeep
touch /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/data/summaries/.gitkeep
touch /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/src/__init__.py
```

- [ ] **Step 6: 安装依赖并验证**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && pip install -r requirements.txt
```

- [ ] **Step 7: 验证目录结构**

```bash
ls -la /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/
```
Expected: 看到 .gitignore, .env.example, requirements.txt, config/, data/, src/ 目录

- [ ] **Step 8: Commit**

```bash
git add .gitignore .env.example requirements.txt config/channels.yaml src/__init__.py data/
git commit -m "chore: initialize project scaffold"
```

---

### Task 2: storage 模块 — JSON/Markdown 读写

**Files:**
- Create: `tests/test_storage.py`
- Create: `src/storage.py`

- [ ] **Step 1: 编写失败测试 — 保存 JSON 文件**

```python
# tests/test_storage.py
import json
import os
import tempfile
from src.storage import save_raw_messages, load_raw_messages, save_summary

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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_storage.py::test_save_raw_messages -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'src.storage'`

- [ ] **Step 3: 实现 save_raw_messages**

```python
# src/storage.py
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_storage.py::test_save_raw_messages -v
```
Expected: PASS

- [ ] **Step 5: 添加测试 — save_summary**

```python
# 在 tests/test_storage.py 末尾追加

def test_save_summary():
    summary_md = "# TG 日报 — 2026-06-08\n\n## AI 技术\n测试内容"
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = save_summary(summary_md, date_str="2026-06-08", base_dir=tmpdir)
        assert os.path.exists(filepath)
        assert filepath.endswith("tg_summary_2026-06-08.md")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        assert "TG 日报" in content
```

- [ ] **Step 6: 运行测试确认失败**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_storage.py::test_save_summary -v
```
Expected: FAIL — `NameError: name 'save_summary' is not defined`

- [ ] **Step 7: 实现 save_summary**

```python
# 在 src/storage.py 末尾追加

def save_summary(content: str, date_str: str, base_dir: str = "data/summaries") -> str:
    """Save summary Markdown to a date-named file."""
    os.makedirs(base_dir, exist_ok=True)
    filename = f"tg_summary_{date_str}.md"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
```

- [ ] **Step 8: 运行全部 storage 测试**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_storage.py -v
```
Expected: 2 PASS

- [ ] **Step 9: Commit**

```bash
git add tests/test_storage.py src/storage.py
git commit -m "feat: add storage module with JSON and Markdown I/O"
```

---

### Task 3: dedup 模块 — 消息去重

**Files:**
- Create: `tests/test_dedup.py`
- Create: `src/dedup.py`

- [ ] **Step 1: 编写失败测试 — 按 msg_id 去重**

```python
# tests/test_dedup.py
from src.dedup import deduplicate

def test_dedup_by_msg_id():
    messages = [
        {"msg_id": 1, "text": "hello", "content_hash": "abc"},
        {"msg_id": 2, "text": "world", "content_hash": "def"},
        {"msg_id": 1, "text": "hello", "content_hash": "abc"},  # 重复 msg_id
    ]
    result = deduplicate(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert ids == [1, 2]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_dedup.py::test_dedup_by_msg_id -v
```
Expected: FAIL

- [ ] **Step 3: 实现 deduplicate 函数**

```python
# src/dedup.py
import hashlib
from typing import List, Dict, Any


def deduplicate(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate messages: first by msg_id, then by content hash."""
    # Step 1: dedup by msg_id
    seen_ids = set()
    id_deduped = []
    for msg in messages:
        if msg["msg_id"] not in seen_ids:
            seen_ids.add(msg["msg_id"])
            id_deduped.append(msg)

    # Step 2: dedup by content_hash (MD5 of text)
    seen_hashes = set()
    result = []
    for msg in id_deduped:
        if msg["content_hash"] not in seen_hashes:
            seen_hashes.add(msg["content_hash"])
            result.append(msg)

    return result
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_dedup.py::test_dedup_by_msg_id -v
```
Expected: PASS

- [ ] **Step 5: 添加测试 — 按 content_hash 跨频道去重**

```python
# 在 tests/test_dedup.py 末尾追加

def test_dedup_by_content_hash():
    messages = [
        {"msg_id": 1, "text": "same content here", "content_hash": "aaa111"},
        {"msg_id": 2, "text": "unique message", "content_hash": "bbb222"},
        {"msg_id": 3, "text": "same content here", "content_hash": "aaa111"},  # 不同 msg_id，相同内容
    ]
    result = deduplicate(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert 1 in ids or 3 in ids  # 保留第一个遇到的
    assert 2 in ids
```

- [ ] **Step 6: 运行全部 dedup 测试**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_dedup.py -v
```
Expected: 2 PASS

- [ ] **Step 7: Commit**

```bash
git add tests/test_dedup.py src/dedup.py
git commit -m "feat: add dedup module with msg_id and content hash deduplication"
```

---

### Task 4: filter 模块 — 广告过滤

**Files:**
- Create: `tests/test_filter.py`
- Create: `src/filter.py`

- [ ] **Step 1: 编写失败测试 — 过滤含营销关键词的消息**

```python
# tests/test_filter.py
from src.filter import filter_ads

def test_filter_marketing_keywords():
    messages = [
        {"msg_id": 1, "text": "GPT-5 今天发布了新版本", "link": "https://t.me/test/1"},
        {"msg_id": 2, "text": "限时优惠！扫码加入获取免费课程", "link": "https://t.me/test/2"},
        {"msg_id": 3, "text": "AI 行业最新动态汇总", "link": "https://t.me/test/3"},
        {"msg_id": 4, "text": "立即购买享五折优惠", "link": "https://t.me/test/4"},
    ]
    result = filter_ads(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert ids == [1, 3]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_filter.py::test_filter_marketing_keywords -v
```
Expected: FAIL

- [ ] **Step 3: 实现 filter_ads 函数**

```python
# src/filter.py
import re
from typing import List, Dict, Any

# 营销关键词列表
MARKETING_KEYWORDS = [
    "限时优惠", "立即购买", "扫码加入", "免费领取",
    "点击购买", "限时折扣", "特价促销", "名额有限",
    "赶紧上车", "手慢无", "最后一天",
]

# 常见推广/短链接域名
PROMOTION_DOMAINS = [
    "bit.ly", "t.co", "ow.ly", "tinyurl.com",
    "shorturl.at", "is.gd", "buff.ly",
]


def _has_promotion_link(text: str) -> bool:
    """Check if text contains promotional links."""
    for domain in PROMOTION_DOMAINS:
        if domain in text:
            return True
    return False


def _has_marketing_keywords(text: str) -> bool:
    """Check if text contains marketing keywords."""
    for kw in MARKETING_KEYWORDS:
        if kw in text:
            return True
    return False


def filter_ads(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out messages that contain promotional links or marketing language."""
    return [
        msg for msg in messages
        if not _has_marketing_keywords(msg.get("text", ""))
        and not _has_promotion_link(msg.get("text", ""))
    ]
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_filter.py::test_filter_marketing_keywords -v
```
Expected: PASS

- [ ] **Step 5: 添加测试 — 过滤含推广链接的消息**

```python
# 在 tests/test_filter.py 末尾追加

def test_filter_promotion_links():
    messages = [
        {"msg_id": 1, "text": "技术分享：如何优化数据库性能", "link": "https://t.me/test/1"},
        {"msg_id": 2, "text": "快来 https://bit.ly/abc123 领取福利", "link": "https://t.me/test/2"},
        {"msg_id": 3, "text": "最新 AI 论文解读", "link": "https://t.me/test/3"},
    ]
    result = filter_ads(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert ids == [1, 3]


def test_filter_empty_text():
    messages = [
        {"msg_id": 1, "text": "", "link": "https://t.me/test/1"},
    ]
    result = filter_ads(messages)
    assert len(result) == 1  # 空文本不过滤
```

- [ ] **Step 6: 运行全部 filter 测试**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_filter.py -v
```
Expected: 3 PASS

- [ ] **Step 7: Commit**

```bash
git add tests/test_filter.py src/filter.py
git commit -m "feat: add filter module for ad and promotion detection"
```

---

### Task 5: fetcher 模块 — Telegram 消息拉取

**Files:**
- Create: `src/fetcher.py`

注意：此模块依赖真实 Telegram 凭证，不做自动化单元测试，仅手动验证。

- [ ] **Step 1: 实现 fetch_messages 函数**

```python
# src/fetcher.py
import os
import hashlib
import yaml
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, FloodWaitError
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_FILE = "tg_session"


def _build_msg_link(channel_username: str, msg_id: int) -> str:
    """Build a t.me permalink for a message."""
    clean = channel_username.lstrip("@").replace("https://t.me/", "")
    return f"https://t.me/{clean}/{msg_id}"


def _compute_content_hash(text: str) -> str:
    """Compute MD5 hash of message text for dedup."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_channels(config_path: str = "config/channels.yaml") -> List[Dict[str, str]]:
    """Load channel list from config file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"配置文件不存在: {config_path}\n"
            f"请复制 config/channels.example.yaml 为 channels.yaml 并填写频道"
        )
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    channels = data.get("channels", [])
    if not channels:
        raise ValueError("channels.yaml 中没有配置任何频道")
    return channels


async def fetch_messages(
    channels: List[Dict[str, str]],
    hours: int = 24,
) -> List[Dict[str, Any]]:
    """
    Fetch messages from configured Telegram channels within the last N hours.

    Args:
        channels: List of {"username": "...", "label": "..."} dicts
        hours: Time window in hours

    Returns:
        List of standardized message dicts
    """
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()

    all_messages = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    for ch in channels:
        username = ch["username"]
        label = ch.get("label", username)

        try:
            entity = await client.get_entity(username)
            async for msg in client.iter_messages(entity, offset_date=cutoff, reverse=False):
                if msg.message:
                    all_messages.append({
                        "msg_id": msg.id,
                        "channel": username,
                        "label": label,
                        "date": msg.date.isoformat(),
                        "text": msg.message,
                        "link": _build_msg_link(username, msg.id),
                        "content_hash": _compute_content_hash(msg.message),
                    })
        except (ChannelPrivateError, ValueError) as e:
            print(f"[WARN] 频道 {username} 无法访问，已跳过: {e}")
        except FloodWaitError as e:
            print(f"[WARN] 频道 {username} 触发频控，等待 {e.seconds}s 后跳过")
        except Exception as e:
            print(f"[WARN] 频道 {username} 拉取异常，已跳过: {e}")

    await client.disconnect()
    return all_messages
```

- [ ] **Step 2: 验证语法正确**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -c "from src.fetcher import fetch_messages, load_channels; print('OK')"
```
Expected: `OK`（可能提示需要安装依赖，如有报错按提示修复）

- [ ] **Step 3: Commit**

```bash
git add src/fetcher.py
git commit -m "feat: add fetcher module for Telegram message pulling"
```

---

### Task 6: summarizer 模块 — OpenAI 中文摘要

**Files:**
- Create: `tests/test_summarizer.py`
- Create: `src/summarizer.py`

- [ ] **Step 1: 编写失败测试 — prompt 构建**

```python
# tests/test_summarizer.py
from src.summarizer import build_summary_prompt, parse_summary_response

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
    assert "按主题分类" in prompt
    assert len(prompt) > 100
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_summarizer.py::test_build_summary_prompt -v
```
Expected: FAIL

- [ ] **Step 3: 实现 build_summary_prompt**

```python
# src/summarizer.py
import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def build_summary_prompt(messages: List[Dict[str, Any]], date_str: str) -> str:
    """Build the OpenAI prompt for Chinese daily digest generation."""
    # 构建消息列表文本
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
```

- [ ] **Step 4: 运行 prompt 测试**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/test_summarizer.py::test_build_summary_prompt -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_summarizer.py src/summarizer.py
git commit -m "feat: add summarizer module with OpenAI Chinese digest generation"
```

---

### Task 7: main.py — CLI 编排入口

**Files:**
- Create: `main.py`

- [ ] **Step 1: 编写 main.py**

```python
# main.py
"""
tg-ai-daily — Telegram 频道日报生成工具

Usage:
    python main.py              # 拉取过去 24h 消息并生成日报
    python main.py --hours 48   # 拉取过去 48h 消息
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime, timezone

from src.fetcher import fetch_messages, load_channels
from src.dedup import deduplicate
from src.filter import filter_ads
from src.summarizer import generate_summary
from src.storage import save_raw_messages, save_summary


def parse_args():
    parser = argparse.ArgumentParser(description="Telegram 频道日报生成工具")
    parser.add_argument("--hours", type=int, default=24, help="拉取最近多少小时的消息 (默认: 24)")
    parser.add_argument("--config", type=str, default="config/channels.yaml", help="频道配置文件路径")
    return parser.parse_args()


async def main():
    args = parse_args()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"[INFO] 开始拉取 Telegram 消息（最近 {args.hours} 小时）...")

    # Step 1: 加载频道配置
    try:
        channels = load_channels(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # Step 2: 拉取消息
    messages = await fetch_messages(channels, hours=args.hours)
    print(f"[INFO] 拉取到 {len(messages)} 条原始消息")

    if not messages:
        print("[INFO] 没有新消息，退出")
        return

    # Step 3: 去重
    before_dedup = len(messages)
    messages = deduplicate(messages)
    print(f"[INFO] 去重: {before_dedup} → {len(messages)} (移除 {before_dedup - len(messages)} 条)")

    # Step 4: 过滤广告
    before_filter = len(messages)
    messages = filter_ads(messages)
    print(f"[INFO] 过滤广告: {before_filter} → {len(messages)} (移除 {before_filter - len(messages)} 条)")

    # Step 5: 保存原始数据
    raw_path = save_raw_messages(messages, today)
    print(f"[INFO] 原始数据已保存: {raw_path}")

    # Step 6: 生成摘要
    print(f"[INFO] 正在调用 OpenAI 生成 {today} 日报...")
    summary_md = generate_summary(messages, today)

    # Step 7: 保存摘要
    summary_path = save_summary(summary_md, today)
    print(f"[INFO] 日报已保存: {summary_path}")

    print(f"[INFO] ✅ 完成！共处理 {len(messages)} 条消息")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 验证语法正确**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -c "import main; print('main.py OK')"
```
Expected: `main.py OK`

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main CLI entry point orchestrating the full pipeline"
```

---

### Task 8: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: 编写 README.md**

```bash
cat > /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily/README.md << 'EOF'
# tg-ai-daily

Telegram 频道日报生成工具 — 拉取配置的频道过去 24 小时消息，通过 OpenAI 生成按主题分类的中文日报。

## 功能

- 📡 通过 Telethon 拉取 Telegram 频道消息
- 🔄 按消息 ID + 内容哈希双重去重
- 🚫 自动过滤广告和推广内容
- 🤖 调用 OpenAI API 生成中文日报摘要
- 📂 原始消息 JSON + 日报 Markdown 按日期存储

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入你的 TG_API_ID, TG_API_HASH, OPENAI_API_KEY
```

### 3. 配置频道
```bash
# 编辑 config/channels.yaml，添加要监控的频道
```

示例：
```yaml
channels:
  - username: "@ai_news_cn"
    label: "AI 新闻"
  - username: "https://t.me/tech_daily"
    label: "科技日报"
```

### 4. 运行
```bash
python main.py              # 拉取最近 24h
python main.py --hours 48   # 拉取最近 48h
```

首次运行会提示登录 Telegram（需要手机号验证码），之后会缓存 session 无需重复登录。

## 目录结构

```
tg-ai-daily/
├── main.py                 # CLI 入口
├── config/channels.yaml    # 频道配置
├── src/                    # 源代码
│   ├── fetcher.py          # 消息拉取
│   ├── dedup.py            # 去重
│   ├── filter.py           # 广告过滤
│   ├── summarizer.py       # OpenAI 摘要
│   └── storage.py          # 读写存储
├── data/raw/               # 原始消息 JSON
├── data/summaries/         # 日报 Markdown
└── tests/                  # 单元测试
```

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `TG_API_ID` | ✅ | Telegram API ID（my.telegram.org） |
| `TG_API_HASH` | ✅ | Telegram API Hash |
| `OPENAI_API_KEY` | ✅ | OpenAI API Key |
| `OPENAI_BASE_URL` | ❌ | API 代理地址（默认官方） |
| `OPENAI_MODEL` | ❌ | 模型名（默认 gpt-4o-mini） |

## License

MIT
EOF
```

- [ ] **Step 2: 运行全部测试确认项目健康**

```bash
cd /Users/xinbiyou/Desktop/Project/MY_PROJECT/tg-ai-daily && python -m pytest tests/ -v
```
Expected: 所有测试 PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```
