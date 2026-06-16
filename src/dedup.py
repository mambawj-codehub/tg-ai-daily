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

    # Step 2: dedup by content_hash
    seen_hashes = set()
    result = []
    for msg in id_deduped:
        if msg["content_hash"] not in seen_hashes:
            seen_hashes.add(msg["content_hash"])
            result.append(msg)

    return result
