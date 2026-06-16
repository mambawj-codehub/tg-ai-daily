from src.dedup import deduplicate


def test_dedup_by_msg_id():
    messages = [
        {"msg_id": 1, "text": "hello", "content_hash": "abc"},
        {"msg_id": 2, "text": "world", "content_hash": "def"},
        {"msg_id": 1, "text": "hello", "content_hash": "abc"},
    ]
    result = deduplicate(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert ids == [1, 2]


def test_dedup_by_content_hash():
    messages = [
        {"msg_id": 1, "text": "same content here", "content_hash": "aaa111"},
        {"msg_id": 2, "text": "unique message", "content_hash": "bbb222"},
        {"msg_id": 3, "text": "same content here", "content_hash": "aaa111"},
    ]
    result = deduplicate(messages)
    assert len(result) == 2
    ids = [m["msg_id"] for m in result]
    assert 1 in ids or 3 in ids
    assert 2 in ids
