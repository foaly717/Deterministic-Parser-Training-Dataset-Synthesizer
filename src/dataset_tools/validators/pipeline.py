from dataclasses import dataclass, field

from dataset_tools.evidence.preparation import PreparedEvidence
from dataset_tools.validators.command import validate_cli_command
from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.parsers.cli_parser import parse_cli_command
from dataset_tools.validators.options import validate_options
from dataset_tools.validators.structure import validate_candidate_structure


@dataclass
class ValidationResult:
    status: str
    stage: str
    validation_logs: list[str] = field(default_factory=list)
    reason_code: str | None = None


def validate_candidate(
    item: dict,
    prepared: PreparedEvidence,
) -> ValidationResult:
    """Run candidate validation against prepared authoritative evidence."""

    if not validate_candidate_structure(item):
        return ValidationResult(
            status="rejected",
            stage="structure",
            reason_code="INVALID_STRUCTURE",
            validation_logs=["Structural validation failed."],
        )

    logs = ["Structural validation passed."]

    parsed_command = parse_cli_command(
        item["response"],
    )

    command_failure = validate_cli_command(
        parsed_command,
        prepared.expected_tool,
    )

    if command_failure:
        logs.append(command_failure.message)
        return ValidationResult(
            status="rejected",
            stage="command",
            reason_code="UNEXPECTED_EXECUTABLE",
            validation_logs=logs,
        )

    option_ok, option_message = validate_options(
        parsed_command,
        valid_options=prepared.valid_options,
    )

    logs.append(option_message)

    if not option_ok:
        return ValidationResult(
            status="rejected",
            stage="options",
            reason_code="UNSUPPORTED_OPTION",
            validation_logs=logs,
        )

    constraint_failure = validate_constraints(
        parsed_command,
        prepared.constraints,
    )

    if constraint_failure:
        logs.append(constraint_failure.message)
        return ValidationResult(
            status="rejected",
            stage="constraints",
            reason_code="UNSUPPORTED_ENUM_VALUE",
            validation_logs=logs,
        )

    return ValidationResult(
        status="accepted",
        stage="complete",
        reason_code=None,
        validation_logs=logs,
    )
