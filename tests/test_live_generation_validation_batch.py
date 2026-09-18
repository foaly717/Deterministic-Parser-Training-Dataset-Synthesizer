import json
from pathlib import Path

from scripts.live_generation_validation_batch import main, OUTPUT


def test_live_generation_validation_batch_records_results(tmp_path, monkeypatch):
    output_path = tmp_path / "results.jsonl"

    monkeypatch.setattr(
        "scripts.live_generation_validation_batch.OUTPUT",
        output_path,
    )

    main()

    assert output_path.exists()

    records = [
        json.loads(line)
        for line in output_path.read_text().splitlines()
    ]

    assert len(records) == 4

    accepted = [
        r for r in records
        if r["status"] == "accepted"
    ]

    rejected = [
        r for r in records
        if r["status"] == "rejected"
    ]

    assert len(accepted) == 2
    assert len(rejected) == 2

    reasons = {
        r["reason_code"]
        for r in rejected
    }

    assert "UNSUPPORTED_ENUM_VALUE" in reasons
    assert "UNSUPPORTED_OPTION" in reasons

    for record in rejected:
        assert record["validation_logs"]
        assert record["candidate"]["response"]
