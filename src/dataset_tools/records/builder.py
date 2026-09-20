"""Construction of canonical RunRecord objects."""

import hashlib

from dataset_tools.candidates.parser import (
    InvalidShapeError,
    MalformedJSONError,
    parse_candidate,
)
from dataset_tools.evidence.preparation import PreparedEvidence
from dataset_tools.records.model import (
    CandidateModel,
    RunRecord,
    ValidationBlock,
    ValidationStage,
    example_id,
    normalize_text,
)
from dataset_tools.validators.pipeline import ValidationResult, validate_candidate
from dataset_tools.validators.reason_codes import ValidationReasonCode
from dataset_tools.validators.serialization import (
    serialize_validation_failure,
    serialize_validation_result,
)
from dataset_tools.validators.structure import validate_candidate_structure


def compute_prompt_sha256(prompt: str) -> str:
    """Hash the exact UTF-8 bytes of the rendered generation prompt."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _base_record_kwargs(
    *,
    prepared: PreparedEvidence,
    fact_id: str,
    generator_provider: str,
    generator_model: str,
    max_tokens: int,
    prompt_sha256: str,
    raw_response: str,
) -> dict:
    return {
        "fact_id": fact_id,
        "source_sha256": prepared.document.source_sha256,
        "generator_provider": generator_provider,
        "generator_model": generator_model,
        "max_tokens": max_tokens,
        "prompt_sha256": prompt_sha256,
        "raw_response": raw_response,
    }


def _validation_block_from_result(
    result: ValidationResult,
) -> ValidationBlock:
    return ValidationBlock(
        status=result.status,
        stage=ValidationStage(result.stage),
        reason_code=(
            ValidationReasonCode(result.reason_code)
            if result.reason_code is not None
            else None
        ),
        validation_logs=result.validation_logs,
    )


def build_run_record(
    *,
    prepared: PreparedEvidence,
    fact_id: str,
    prompt: str,
    raw_response: str,
    generator_provider: str,
    generator_model: str,
    max_tokens: int,
) -> RunRecord:
    """Build one canonical record from one successful model invocation.

    Transport/model invocation failures occur before this function and do not
    produce records. A successful empty or malformed model response does
    produce a parse-failure record.
    """
    prompt_sha256 = compute_prompt_sha256(prompt)

    base = _base_record_kwargs(
        prepared=prepared,
        fact_id=fact_id,
        generator_provider=generator_provider,
        generator_model=generator_model,
        max_tokens=max_tokens,
        prompt_sha256=prompt_sha256,
        raw_response=raw_response,
    )

    # Parse boundary.
    try:
        parsed_candidate = parse_candidate(raw_response)
    except MalformedJSONError as exc:
        validation = serialize_validation_failure(
            stage=ValidationStage.PARSE.value,
            reason_code=ValidationReasonCode.INVALID_JSON.value,
            message=str(exc),
        )
        return RunRecord(
            **base,
            candidate=None,
            example_id=None,
            validation=ValidationBlock.model_validate(validation),
        )
    except InvalidShapeError as exc:
        validation = serialize_validation_failure(
            stage=ValidationStage.PARSE.value,
            reason_code=ValidationReasonCode.INVALID_JSON_SHAPE.value,
            message=str(exc),
        )
        return RunRecord(
            **base,
            candidate=None,
            example_id=None,
            validation=ValidationBlock.model_validate(validation),
        )

    # Structural boundary. This intentionally occurs before normalization.
    if not validate_candidate_structure(parsed_candidate):
        validation_result = ValidationResult(
            status="rejected",
            stage=ValidationStage.STRUCTURE.value,
            reason_code=ValidationReasonCode.INVALID_STRUCTURE.value,
            validation_logs=["Structural validation failed."],
        )
        validation = serialize_validation_result(validation_result)
        return RunRecord(
            **base,
            candidate=None,
            example_id=None,
            validation=ValidationBlock.model_validate(validation),
        )

    # Normalize only after structural validation has passed.
    normalized_candidate = {
        "instruction": normalize_text(parsed_candidate["instruction"]),
        "context": normalize_text(parsed_candidate["context"]),
        "response": normalize_text(parsed_candidate["response"]),
    }

    # Structural validation guarantees these required values are strings.
    candidate = CandidateModel.model_validate(normalized_candidate)

    candidate_dict = candidate.model_dump()

    # Domain validation operates on exactly the normalized candidate that is
    # persisted in the RunRecord.
    validation_result = validate_candidate(
        candidate_dict,
        prepared,
    )

    return RunRecord(
        **base,
        candidate=candidate,
        example_id=example_id(
            candidate.instruction,
            candidate.context,
            candidate.response,
        ),
        validation=_validation_block_from_result(validation_result),
    )
