import subprocess

def test_dataset_diversity_runs():
    result = subprocess.run(
        ["uv", "run", "python", "scripts/dataset_diversity.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "DATASET DIVERSITY REPORT" in result.stdout
