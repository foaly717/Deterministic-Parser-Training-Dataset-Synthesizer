import subprocess


def test_option_coverage_runs():
    result = subprocess.run(
        ["uv", "run", "python", "scripts/option_coverage.py"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "OPTION COVERAGE REPORT" in result.stdout
