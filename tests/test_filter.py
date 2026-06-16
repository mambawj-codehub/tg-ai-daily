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
    assert len(result) == 1
