"""Canonical storage-neutral run-record domain models."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from dataset_tools.evidence.ids import deterministic_id
from dataset_tools.validators.reason_codes import ValidationReasonCode


class ValidationStage(str, Enum):
    """Canonical validation pipeline stages persisted in RunRecord."""

    PARSE = "parse"
    STRUCTURE = "structure"
    COMMAND = "command"
    OPTIONS = "options"
    CONSTRAINTS = "constraints"
    COMPLETE = "complete"


class CandidateModel(BaseModel):
    """Canonical persisted representation of a synthesized candidate.

    The model does not normalize values. Normalization is performed by the
    record builder before this model is constructed.
    """

    model_config = ConfigDict(extra="forbid")

    instruction: str = Field(min_length=1)
    context: str | None = None
    response: str = Field(min_length=1)


def normalize_text(text: str | None) -> str | None:
    """Normalize candidate text for persisted identity.

    Rules:
    - CRLF becomes LF.
    - Outer whitespace is stripped using str.strip().
    - Interior whitespace is preserved.
    - A lone CR is preserved.
    - None remains None.

    These rules are part of the example identity contract. Changing them
    requires an identity/schema version change.
    """
    if text is None:
        return None
    return text.replace("\r\n", "\n").strip()


def example_id(
    instruction: str,
    context: str | None,
    response: str,
) -> str:
    """Return deterministic content identity for one normalized candidate.

    Identity is intentionally limited to normalized instruction, context, and
    response. Provenance, validation state, model metadata, and raw output are
    not part of candidate content identity.
    """
    normalized_instruction = normalize_text(instruction)
    normalized_context = normalize_text(context)
    normalized_response = normalize_text(response)

    if normalized_instruction is None:
        raise ValueError("instruction cannot be None")
    if normalized_response is None:
        raise ValueError("response cannot be None")

    return deterministic_id(
        "example",
        normalized_instruction,
        normalized_context,
        normalized_response,
    )


class ValidationBlock(BaseModel):
    """Strict persisted representation of validation outcome."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["accepted", "rejected", "failed"]
    stage: ValidationStage
    reason_code: ValidationReasonCode | None = None
    validation_logs: list[str] = Field(default_factory=list)


class RunRecord(BaseModel):
    """Canonical storage-neutral record for one generation attempt."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = Field(default=1, frozen=True)
    fact_id: str
    source_sha256: str
    generator_provider: str
    generator_model: str
    max_tokens: int = Field(ge=1)
    prompt_sha256: str
    raw_response: str
    example_id: str | None = None
    candidate: CandidateModel | None = None
    validation: ValidationBlock

    @model_validator(mode="after")
    def verify_self_invariants(self) -> "RunRecord":
        if (self.candidate is None) != (self.example_id is None):
            raise ValueError(
                "candidate and example_id must either both be present or both be None"
            )

        if self.candidate is not None and self.example_id is not None:
            normalized_instruction = normalize_text(
                self.candidate.instruction
            )
            normalized_context = normalize_text(
                self.candidate.context
            )
            normalized_response = normalize_text(
                self.candidate.response
            )

            if self.candidate.instruction != normalized_instruction:
                raise ValueError(
                    "Candidate instruction is not normalized"
                )

            if self.candidate.context != normalized_context:
                raise ValueError(
                    "Candidate context is not normalized"
                )

            if self.candidate.response != normalized_response:
                raise ValueError(
                    "Candidate response is not normalized"
                )

            recomputed = example_id(
                self.candidate.instruction,
                self.candidate.context,
                self.candidate.response,
            )

            if recomputed != self.example_id:
                raise ValueError(
                    "Stored example_id does not match candidate content identity"
                )

        return self
