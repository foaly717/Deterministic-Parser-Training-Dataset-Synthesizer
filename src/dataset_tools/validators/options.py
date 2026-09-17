import re

OPTION_RE = re.compile(r"(?<!\S)--?[A-Za-z0-9][A-Za-z0-9-]*")


def validate_cli_response(
    response: str,
    valid_options: set[str],
) -> tuple[bool, str]:
    """Ensures every flag in the generated response exists in the authoritative evidence."""
    extracted_flags = set(OPTION_RE.findall(response))

    if not extracted_flags:
        return True, "No CLI flags detected in response."

    invalid_flags = extracted_flags - valid_options

    if invalid_flags:
        return False, f"Unsupported options detected: {sorted(invalid_flags)}"

    return True, "All detected options are supported by supplied evidence."
