"""
tg-ai-daily — Telegram 频道日报生成工具

Usage:
    python main.py              # 拉取过去 24h 消息并生成日报
    python main.py --hours 48   # 拉取过去 48h 消息
"""

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
