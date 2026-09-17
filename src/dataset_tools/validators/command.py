import re


COMMAND_TOKEN_RE = re.compile(r"^[A-Za-z0-9_./-]+$")


def validate_cli_command(
    response: str,
    expected_tool: str,
) -> tuple[bool, str]:
    """Validate that a response is a single command using the expected executable."""
    command = response.strip()

    if not command:
        return False, "Response is empty."

    if "\n" in command:
        return False, "Response must contain exactly one terminal command."

    parts = command.split()

    if not parts:
        return False, "Response does not contain a command."

    executable = parts[0]

    if not COMMAND_TOKEN_RE.fullmatch(executable):
        return False, f"Invalid executable token: {executable!r}"

    if executable != expected_tool:
        return False, f"Unexpected executable detected: {executable!r}"

    return True, "Expected executable detected."
