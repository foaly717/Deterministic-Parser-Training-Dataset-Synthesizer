import json
import uuid
from pathlib import Path

from dataset_tools.schema import TrainingExample


REQUIRED_FIELDS = {"instruction", "context", "response"}


def validate_candidate_structure(item: dict) -> bool:
    """Accept only structurally usable model output."""
    if not isinstance(item, dict):
        return False
    if not REQUIRED_FIELDS.issubset(item):
        return False

    instruction = item["instruction"]
    response = item["response"]
    context = item["context"]

    if not isinstance(instruction, str) or not instruction.strip():
        return False
    if not isinstance(response, str) or not response.strip():
        return False
    if context is not None and not isinstance(context, str):
        return False

    return True


def save_candidates(
    raw_responses: list[dict],
    source_sha256: str,
    generator_model: str,
    output_path: Path = Path("data/raw/candidates.jsonl"),
) -> int:
    """Append structurally valid candidates to candidates.jsonl."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with output_path.open("a", encoding="utf-8") as handle:
        for item in raw_responses:
            if not validate_candidate_structure(item):
                continue

            example = TrainingExample(
                id=str(uuid.uuid4()),
                instruction=item["instruction"],
                context=item["context"],
                response=item["response"],
                source_sha256=source_sha256,
                generator_model=generator_model,
                status="candidate",
                validation_logs=[],
            )

            record = {
                "id": example.id,
                "instruction": example.instruction,
                "context": example.context,
                "response": example.response,
                "source_sha256": example.source_sha256,
                "generator_model": example.generator_model,
                "status": example.status,
                "validation_logs": example.validation_logs,
            }

            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    return count
