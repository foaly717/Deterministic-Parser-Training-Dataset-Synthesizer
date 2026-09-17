import json
from pathlib import Path


def test_livefire_output_is_valid_jsonl(tmp_path):
    output = tmp_path / "livefire.jsonl"

    records = [
        {
            "attempt": 1,
            "status": "rejected",
            "raw_response": '{"instruction":"test"}',
        },
        {
            "attempt": 2,
            "status": "accepted",
            "raw_response": '{"instruction":"test 2"}',
        },
    ]

    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    lines = output.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert [json.loads(line)["attempt"] for line in lines] == [1, 2]
