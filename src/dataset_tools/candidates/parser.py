import json
from typing import Any


class CandidateParseError(ValueError):
    """Raised when model output is not valid JSON containing one object."""


def parse_candidate(raw_output: str) -> dict[str, Any]:
    """Decode raw model output as exactly one top-level JSON object.

    This function performs serialization-level parsing only. It does not
    validate the candidate schema, required fields, field types, or semantic
    validity. Those checks belong to candidate validation.
    """

    try:
        candidate = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise CandidateParseError(
            f"Model output is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(candidate, dict):
        raise CandidateParseError(
            "Model output must be exactly one JSON object."
        )

    return candidate
