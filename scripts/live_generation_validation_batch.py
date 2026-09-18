from pathlib import Path
import json
import uuid

from dataset_tools.evidence.loaders.handbrakecli import HandBrakeCliLoader
from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.validators.pipeline import validate_candidate
from dataset_tools.validators.serialization import serialize_validation_result


OUTPUT = Path("data/raw/live_validation_results.jsonl")


PROMPTS = [
    {
        "expected": "accepted",
        "instruction": (
            "Generate a HandBrakeCLI command to convert "
            "input.mkv to output.mp4 using x265."
        ),
    },
    {
        "expected": "accepted",
        "instruction": (
            "Generate a HandBrakeCLI command to convert "
            "input.mkv to output.mp4 using the mp4 container."
        ),
    },
    {
        "expected": "rejected",
        "instruction": (
            "Generate a HandBrakeCLI command using an imaginary codec."
        ),
    },
    {
        "expected": "rejected",
        "instruction": (
            "Generate a HandBrakeCLI command using an unsupported option."
        ),
    },
]


def fake_generation(prompt: str) -> str:
    """
    Replace this function with the real model call.
    Keep validation loop unchanged.
    """

    if "x265" in prompt:
        return (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--format av_mp4 "
            "--encoder x265"
        )

    if "mp4 container" in prompt:
        return (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--format av_mp4 "
            "--encoder x264"
        )

    if "imaginary codec" in prompt:
        return (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--encoder imaginary_codec"
        )

    if "unsupported option" in prompt:
        return (
            "HandBrakeCLI "
            "--input input.mkv "
            "--output output.mp4 "
            "--fake-option yes"
        )

    raise RuntimeError("No generation fixture matched")


def main():
    evidence_path = Path(
        "data/evidence/handbrakecli-help.txt"
    )

    doc = HandBrakeCliLoader().load(evidence_path)

    constraints = extract_constraints(doc)

    evidence_index = build_evidence_index(
        doc,
        constraints,
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8",
    ) as handle:

        for item in PROMPTS:
            response = fake_generation(
                item["instruction"]
            )

            candidate = {
                "instruction": item["instruction"],
                "context": None,
                "response": response,
            }

            result = validate_candidate(
                candidate,
                "HandBrakeCLI",
                evidence_index,
            )

            validation = serialize_validation_result(
                result,
            )

            record = {
                "id": str(uuid.uuid4()),
                "expected": item["expected"],
                "candidate": candidate,
                "validation": validation,
            }

            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

            print(
                result.status,
                "::",
                result.stage,
                "::",
                item["instruction"],
            )

            if result.reason_code:
                print(
                    "  reason:",
                    result.reason_code,
                )

            for log in result.validation_logs:
                print(
                    "  log:",
                    log,
                )


if __name__ == "__main__":
    main()
