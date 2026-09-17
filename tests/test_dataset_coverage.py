import subprocess


def test_dataset_coverage_runs():
    result = subprocess.run(
        ["uv", "run", "python", "scripts/dataset_coverage.py"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "DATASET COVERAGE REPORT" in result.stdout
