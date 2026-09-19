from dataset_tools.parsers.command import ParsedCommand


def validate_options(
    command: ParsedCommand,
    valid_options: frozenset[str],
) -> tuple[bool, str]:
    """Validate parsed CLI options against prepared evidence."""

    extracted_flags = {
        option.name
        for option in command.options
    }

    if not extracted_flags:
        return True, "No CLI flags detected in response."

    invalid_flags = extracted_flags - valid_options

    if invalid_flags:
        return (
            False,
            f"Unsupported options detected: {sorted(invalid_flags)}",
        )

    return True, "All detected options are supported by supplied evidence."
