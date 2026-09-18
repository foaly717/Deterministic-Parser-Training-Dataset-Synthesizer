from pathlib import Path
import json

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.validators.pipeline import validate_candidate
from dataset_tools.evidence.index import build_evidence_index


PROMPTS = [
    "Convert input.mkv to output.mp4 using x265.",
    "Convert input.mkv to output.mkv using H.264.",
    "Convert input.mkv to output.mp4 using the av_mp4 container.",
    "Convert input.mkv to output.mp4 with quality 22.",
    "Convert input.mkv to output.mp4 with stereo audio.",
    "Convert input.mkv to output.mp4 using VP9.",
    "Convert input.mkv to output.mp4 using an imaginary codec.",
    "Convert input.mkv to output.mp4 using encoder x265_10bit.",
    "Convert input.mkv to output.mp4 with invalid format fake_container.",
]


# Temporary candidates.
# Replace this function with model generation once the validator loop is proven.
def generate_candidate(prompt: str) -> str:
    mapping = {
        PROMPTS[0]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --format av_mp4 \\
  --encoder x265""",

        PROMPTS[1]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mkv \\
  --encoder x264""",

        PROMPTS[2]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --format av_mp4""",

        PROMPTS[3]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --quality 22""",

        PROMPTS[4]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --mixdown stereo""",

        PROMPTS[5]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --encoder VP9""",

        PROMPTS[6]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --encoder imaginary_codec""",

        PROMPTS[7]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --encoder x265_10bit""",

        PROMPTS[8]: """HandBrakeCLI \\
  --input input.mkv \\
  --output output.mp4 \\
  --format fake_container""",
    }

    return mapping[prompt]


def main():
    evidence_path = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(evidence_path)
    constraints = extract_constraints(document)

    index = build_evidence_index(
        document,
        constraints=constraints,
    )

    results = []

    for prompt in PROMPTS:
        response = generate_candidate(prompt)

        candidate = {
            "prompt": prompt,
            "response": response,
        }

        result = validate_candidate(
            candidate,
            expected_tool="HandBrakeCLI",
            evidence_index=index,
        )

        record = {
            "prompt": prompt,
            "response": response,
            "passed": result.passed,
            "stage": result.stage,
            "logs": result.logs,
        }

        results.append(record)

        print("=" * 80)
        print(prompt)
        print()
        print(response)
        print()
        print("PASS" if result.passed else "FAIL")
        print(result.stage)
        for log in result.logs:
            print(" -", log)

    output = Path("handbrake_generation_validation_results.json")
    output.write_text(
        json.dumps(results, indent=2)
    )

    print()
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
