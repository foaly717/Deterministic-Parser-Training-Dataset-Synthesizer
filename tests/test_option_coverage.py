import subprocess
from pathlib import Path


def test_option_coverage_runs():
    fixture = Path("tests/fixtures/sample_dataset.jsonl")
    evidence = Path("data/evidence/handbrakecli-help.txt")

    result = subprocess.run(
        [
            "uv", "run", "python",
            "scripts/option_coverage.py",
            "--input", str(fixture),
            "--evidence", str(evidence),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "OPTION COVERAGE REPORT" in result.stdout
    assert "Documented options:" in result.stdout
    assert "Observed:" in result.stdout
    assert "Uncovered:" in result.stdout
    assert "--preset" in result.stdout
