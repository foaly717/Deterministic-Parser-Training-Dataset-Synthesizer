import re
import shlex

from dataset_tools.validators.failures import ValidationFailure
from dataset_tools.validators.reason_codes import ValidationReasonCode


def validate_constraints(
    response: str,
    constraints: dict[str, set[str]],
) -> ValidationFailure | None:
    tokens = shlex.split(response)

    for subject, allowed_values in constraints.items():
        for index, token in enumerate(tokens):
            if token != subject:
                continue

            if index + 1 >= len(tokens):
                continue

            value = tokens[index + 1].strip("\"'")

            if value not in allowed_values:
                return ValidationFailure(
                    ValidationReasonCode.UNSUPPORTED_ENUM_VALUE,
                    f"Unsupported value for {subject}: {value}",
                )

    return None
