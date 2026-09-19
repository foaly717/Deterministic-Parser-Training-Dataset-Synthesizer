from dataset_tools.evidence.schema import EnumConstraint
from dataset_tools.parsers.cli_parser import parse_cli_command
from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.validators.reason_codes import ValidationReasonCode


def test_documented_enum_value_is_accepted():
    command = parse_cli_command(
        'ExampleCLI --mode "alpha"'
    )

    constraints = (
        EnumConstraint(
            constraint_id="enum-mode",
            target_entity="--mode",
            source_fact_ids=[],
            allowed_values=[
                "alpha",
                "beta",
                "delta",
            ],
        ),
    )

    failure = validate_constraints(
        command,
        constraints,
    )

    assert failure is None


def test_fabricated_enum_value_is_rejected():
    command = parse_cli_command(
        'ExampleCLI --mode "gamma"'
    )

    constraints = (
        EnumConstraint(
            constraint_id="enum-mode",
            target_entity="--mode",
            source_fact_ids=[],
            allowed_values=[
                "alpha",
                "beta",
                "delta",
            ],
        ),
    )

    failure = validate_constraints(
        command,
        constraints,
    )

    assert failure is not None
    assert failure.reason_code == (
        ValidationReasonCode.UNSUPPORTED_ENUM_VALUE
    )
