import subprocess
from pathlib import Path


def test_dataset_coverage_runs():
    fixture = Path("tests/fixtures/sample_dataset.jsonl")

    result = subprocess.run(
        [
            "uv", "run", "python",
            "scripts/dataset_coverage.py",
            "--input", str(fixture),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "DATASET COVERAGE REPORT" in result.stdout
    assert "Records: 3" in result.stdout
    assert "accepted: 2" in result.stdout
    assert "rejected: 1" in result.stdout
    assert "--preset" in result.stdout
