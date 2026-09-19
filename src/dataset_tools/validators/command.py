from dataset_tools.parsers.command import ParsedCommand
from dataset_tools.validators.failures import ValidationFailure
from dataset_tools.validators.reason_codes import ValidationReasonCode


def validate_cli_command(
    command: ParsedCommand,
    expected_tool: str,
) -> ValidationFailure | None:
    """Validate executable identity from normalized command IR."""

    if command.executable != expected_tool:
        return ValidationFailure(
            ValidationReasonCode.UNEXPECTED_EXECUTABLE,
            f"Unexpected executable detected: {command.executable!r}",
        )

    return None
