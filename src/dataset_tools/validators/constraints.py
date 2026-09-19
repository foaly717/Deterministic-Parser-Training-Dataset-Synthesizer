from dataset_tools.evidence.schema import (
    DerivedConstraint,
    EnumConstraint,
)
from dataset_tools.parsers.command import ParsedCommand
from dataset_tools.validators.failures import ValidationFailure
from dataset_tools.validators.reason_codes import ValidationReasonCode


def validate_constraints(
    command: ParsedCommand,
    constraints: tuple[DerivedConstraint, ...],
) -> ValidationFailure | None:
    """Validate parsed command against evidence-derived constraints."""

    for constraint in constraints:
        if isinstance(constraint, EnumConstraint):
            failure = _validate_enum_constraint(
                command,
                constraint,
            )

            if failure:
                return failure

    return None


def _validate_enum_constraint(
    command: ParsedCommand,
    constraint: EnumConstraint,
) -> ValidationFailure | None:
    for option in command.options:
        if option.name != constraint.target_entity:
            continue

        if option.value is None:
            continue

        if option.value not in constraint.allowed_values:
            return ValidationFailure(
                ValidationReasonCode.UNSUPPORTED_ENUM_VALUE,
                (
                    f"Unsupported value for "
                    f"{constraint.target_entity}: {option.value}"
                ),
            )

    return None
