from pathlib import Path

from dataset_tools.evidence.loaders.handbrakecli import HandBrakeCliLoader
from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.validators.pipeline import validate_candidate


def test_handbrake_generation_positive_and_negative():
    doc = HandBrakeCliLoader().load(
        Path("data/evidence/handbrakecli-help.txt")
    )

    constraints = extract_constraints(doc)

    index = build_evidence_index(
        doc,
        constraints,
    )

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
        "HandBrakeCLI",
        index,
    )

    invalid_result = validate_candidate(
        invalid,
        "HandBrakeCLI",
        index,
    )

    assert valid_result.status == "accepted"

    assert invalid_result.status == "rejected"
    assert invalid_result.stage == "constraints"
    assert invalid_result.reason_code == "UNSUPPORTED_ENUM_VALUE"
