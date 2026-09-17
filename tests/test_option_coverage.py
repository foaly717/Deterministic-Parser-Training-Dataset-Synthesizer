import subprocess


def test_option_coverage_runs():
    result = subprocess.run(
        ["uv", "run", "python", "scripts/option_coverage.py", "--input", "data/raw/livefire_20.jsonl", "--evidence", "data/evidence/handbrakecli-help.txt"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "OPTION COVERAGE REPORT" in result.stdout
