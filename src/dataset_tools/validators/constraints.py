import re

from dataset_tools.validators.failures import ValidationFailure
from dataset_tools.validators.reason_codes import ValidationReasonCode


def validate_constraints(
    response: str,
    constraints: dict[str, set[str]],
) -> ValidationFailure | None:
    for subject, allowed_values in constraints.items():
        pattern = rf"{re.escape(subject)}\s+\"([^\"]+)\""
        matches = re.findall(pattern, response)

        for value in matches:
            if value not in allowed_values:
                return ValidationFailure(
                    ValidationReasonCode.UNSUPPORTED_ENUM_VALUE,
                    f"Unsupported value for {subject}: {value}",
                )

    return None
