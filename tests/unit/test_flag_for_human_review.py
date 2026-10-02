import json

from equipment_request_system.domain.services import flag_for_human_review


def test_writes_review_record(mock_data_dir):
    path = mock_data_dir / "review_queue.json"
    result = flag_for_human_review(
        "E100",
        "I need a specialized monitor",
        "Specialized equipment is not covered",
        "REQ-100",
        path,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert result["status"] == "queued"
    assert saved["requests"][0]["request_id"] == "REQ-100"


def test_duplicate_request_id_is_idempotent(mock_data_dir):
    path = mock_data_dir / "review_queue.json"
    first = flag_for_human_review("E100", "request", "reason", "REQ-200", path)
    second = flag_for_human_review("E100", "request", "reason", "REQ-200", path)

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert first["review"]["review_id"] == second["review"]["review_id"]
    assert second["status"] == "already_queued"
    assert len(saved["requests"]) == 1
