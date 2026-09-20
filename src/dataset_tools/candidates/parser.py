"""Candidate parsing functions and typed failure taxonomy."""

import json
from typing import Any


class CandidateParseError(ValueError):
    """Base exception for candidate parsing failures."""


class MalformedJSONError(CandidateParseError):
    """Raised when raw model output fails JSON decoding."""


class InvalidShapeError(CandidateParseError):
    """Raised when valid JSON is not exactly one top-level object."""


def parse_candidate(raw_output: str) -> dict[str, Any]:
    """Decode raw model output as exactly one top-level JSON object.

    Parsing is deliberately limited to serialization-level validation.
    Candidate schema and semantic validation remain downstream concerns.
    """
    try:
        candidate = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise MalformedJSONError(
            f"Model output is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(candidate, dict):
        raise InvalidShapeError(
            "Model output must be exactly one JSON object."
        )

    return candidate
