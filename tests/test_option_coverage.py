import subprocess


def test_option_coverage_runs():
    result = subprocess.run(
        [
            "uv", "run", "python",
            "scripts/option_coverage.py",
            "--input",
            "data/raw/livefire_50_deterministic.jsonl",
            "--evidence",
            "data/evidence/handbrakecli-help.txt",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "OPTION COVERAGE REPORT" in result.stdout
    assert "Documented options: 151" in result.stdout
    assert "Observed:" in result.stdout
    assert "Uncovered:" in result.stdout
    assert "--preset" in result.stdout
