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
