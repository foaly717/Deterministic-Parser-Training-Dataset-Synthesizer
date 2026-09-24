from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.validators.pipeline import validate_candidate


def test_handbrake_generation_positive_and_negative():
    document = load_evidence(
        Path("data/evidence/handbrakecli-help.txt")
    )

    prepared = prepare_evidence(document)

    valid = {
        "instruction": (
            "Generate a HandBrakeCLI command to convert "
            "input.mkv to output.mp4 using x265."
        ),
        "context": None,
        "response": (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--format av_mp4 "
            "--encoder x265"
        ),
    }

    invalid = {
        "instruction": (
            "Generate a HandBrakeCLI command using "
            "an imaginary codec."
        ),
        "context": None,
        "response": (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--encoder imaginary_codec"
        ),
    }

    valid_result = validate_candidate(
        valid,
        prepared,
    )

    invalid_result = validate_candidate(
        invalid,
        prepared,
    )

    assert valid_result.status == "accepted"

    assert invalid_result.status == "rejected"
    assert invalid_result.stage == "constraints"
    assert invalid_result.reason_code == "UNSUPPORTED_ENUM_VALUE"
