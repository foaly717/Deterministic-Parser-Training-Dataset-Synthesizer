import re


def validate_constraints(
    response: str,
    constraints: dict[str, set[str]],
) -> tuple[bool, str]:
    """Validate that any constrained option values in the response are allowed."""
    for subject, allowed_values in constraints.items():
        pattern = rf"{re.escape(subject)}\s+\"([^\"]+)\""
        matches = re.findall(pattern, response)

        for value in matches:
            if value not in allowed_values:
                return False, f"Unsupported value for {subject}: {value}"

    return True, "All detected constraints are satisfied."
