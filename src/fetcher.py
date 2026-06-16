import os
import hashlib
import yaml
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
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
