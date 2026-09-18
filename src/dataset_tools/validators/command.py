import re

from dataset_tools.validators.failures import ValidationFailure
from dataset_tools.validators.reason_codes import ValidationReasonCode


COMMAND_TOKEN_RE = re.compile(r"^[A-Za-z0-9_./-]+$")


def validate_cli_command(
    response: str,
    expected_tool: str,
) -> ValidationFailure | None:
    command = response.strip()

    if not command:
        return ValidationFailure(
            ValidationReasonCode.INVALID_STRUCTURE,
            "Response is empty.",
        )

    if "\n" in command:
        return ValidationFailure(
            ValidationReasonCode.INVALID_STRUCTURE,
            "Response must contain exactly one terminal command.",
        )

    parts = command.split()

    if not parts:
        return ValidationFailure(
            ValidationReasonCode.INVALID_STRUCTURE,
            "Response does not contain a command.",
        )

    executable = parts[0]

    if not COMMAND_TOKEN_RE.fullmatch(executable):
        return ValidationFailure(
            ValidationReasonCode.UNEXPECTED_EXECUTABLE,
            f"Invalid executable token: {executable!r}",
        )

    if executable != expected_tool:
        return ValidationFailure(
            ValidationReasonCode.UNEXPECTED_EXECUTABLE,
            f"Unexpected executable detected: {executable!r}",
        )

    return None
