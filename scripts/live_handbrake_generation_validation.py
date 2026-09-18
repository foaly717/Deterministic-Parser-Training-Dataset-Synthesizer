from pathlib import Path
import json
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.validators.pipeline import validate_candidate

EVIDENCE = Path("data/evidence/handbrakecli-help.txt")
OUT = Path("data/generation_runs/handbrake_validation_results.jsonl")

PROMPTS = [
    "Generate a HandBrakeCLI command to convert input.mkv to output.mp4 using x265.",
    "Generate a HandBrakeCLI command to encode input.mkv as an mp4 file using h264.",
    "Generate a HandBrakeCLI command to convert movie.mkv to movie.mp4 with av1 encoder.",
    "Generate a HandBrakeCLI command using x265 with constant quality 22.",
    "Generate a HandBrakeCLI command that selects the mp4 container format.",
    "Generate a HandBrakeCLI command that uses an imaginary codec.",
    "Generate a HandBrakeCLI command with an unsupported option --fake-option.",
]

def fake_generation(prompt):
    """Replace with model call once loop is proven."""
    if "imaginary codec" in prompt:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --encoder imaginary_codec"
    elif "unsupported option" in prompt:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --fake-option yes"
    elif "x265" in prompt:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --format av_mp4 --encoder x265"
    elif "h264" in prompt:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --encoder x264"
    elif "av1" in prompt:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --encoder svt_av1"
    else:
        response = "HandBrakeCLI --input input.mkv --output output.mp4 --format av_mp4"

    return {
        "instruction": prompt,
        "context": None,
        "response": response,
    }

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    document = load_evidence(EVIDENCE)
    index = build_evidence_index(document)

    with OUT.open("w", encoding="utf-8") as handle:
        for prompt in PROMPTS:
            candidate = fake_generation(prompt)
            result = validate_candidate(
                candidate,
                expected_tool="HandBrakeCLI",
                evidence_index=index,
            )

            record = {
                "prompt": prompt,
                "response": candidate["response"],
                "status": result.status,
                "stage": result.stage,
                "reason_code": result.reason_code,
                "logs": result.validation_logs,
            }

            print(record["status"], "::", record["stage"], "::", prompt)
            handle.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    main()
