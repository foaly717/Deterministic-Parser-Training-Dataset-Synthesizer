import json
import subprocess
from pathlib import Path


def test_normalize_evidence_runs(tmp_path):
    fixture = Path("data/evidence/handbrakecli-help.txt")
    output = tmp_path / "normalized.json"

    result = subprocess.run(
        [
            "uv", "run", "python",
            "scripts/normalize_evidence.py",
            "--input", str(fixture),
            "--output", str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.returncode == 0
    assert output.exists()

    document = json.loads(output.read_text(encoding="utf-8"))

    assert document["source_id"] == "handbrakecli-help"
    assert document["source_type"] == "handbrakecli"
    assert document["source_sha256"]
    assert document["document_id"]
    assert document["facts"]

    fact = document["facts"][0]
    assert fact["fact_id"]
    assert fact["document_id"] == document["document_id"]
    assert fact["provenance"]["source_id"] == document["source_id"]
