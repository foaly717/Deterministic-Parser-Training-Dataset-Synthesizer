import re

from dataset_tools.validators.reason_codes import ValidationReasonCode


OPTION_RE = re.compile(r"(?<!\S)--?[A-Za-z0-9][A-Za-z0-9_-]*")


def validate_cli_response(
    response: str,
    valid_options: frozenset[str],
) -> tuple[bool, str]:
    """Validate that CLI options exist in prepared evidence."""

    raw_tokens = response.split()
    extracted_flags = set()

    for token in raw_tokens:
        flag_candidate = token.split("=")[0]
        match = OPTION_RE.match(flag_candidate)
        if match:
            extracted_flags.add(match.group(0))

    if not extracted_flags:
        return True, "No CLI flags detected in response."

    invalid_flags = extracted_flags - valid_options

    if invalid_flags:
        return (
            False,
            f"Unsupported options detected: {sorted(invalid_flags)}",
        )

    return True, "All detected options are supported by supplied evidence."
