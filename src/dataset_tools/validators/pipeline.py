from dataclasses import dataclass, field

from dataset_tools.generator.runner import validate_candidate_structure
from dataset_tools.validators.command import validate_cli_command
from dataset_tools.validators.options import validate_cli_response


@dataclass
class ValidationResult:
    status: str
    stage: str
    validation_logs: list[str] = field(default_factory=list)


def validate_candidate(
    item: dict,
    expected_tool: str,
    valid_options: set[str],
) -> ValidationResult:
    """Run candidate validation in deterministic stages."""
    if not validate_candidate_structure(item):
        return ValidationResult(
            status="rejected",
            stage="structure",
            validation_logs=["Structural validation failed."],
        )

    logs = ["Structural validation passed."]

    command_ok, command_message = validate_cli_command(
        item["response"],
        expected_tool,
    )
    logs.append(command_message)

    if not command_ok:
        return ValidationResult(
            status="rejected",
            stage="command",
            validation_logs=logs,
        )

    option_ok, option_message = validate_cli_response(
        item["response"],
        valid_options,
    )
    logs.append(option_message)

    if not option_ok:
        return ValidationResult(
            status="rejected",
            stage="options",
            validation_logs=logs,
        )

    return ValidationResult(
        status="accepted",
        stage="complete",
        validation_logs=logs,
    )
