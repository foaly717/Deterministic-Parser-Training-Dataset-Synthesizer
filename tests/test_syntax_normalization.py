from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.parsers.cli_parser import parse_cli_command
from dataset_tools.validators.options import validate_options


def test_equals_syntax_option_validation():
    valid_options = frozenset({
        "ExampleCLI",
        "--mode",
        "-i",
        "-o",
    })

    ok, msg = validate_options(
        parse_cli_command(
        'ExampleCLI --mode="alpha"',
        ),
        valid_options,
    )

    assert ok is True


def test_equals_syntax_constraint_validation():
    constraints = {"--mode": {"alpha", "beta"}}

    failure = validate_constraints(
        'ExampleCLI --mode="alpha"',
        constraints,
    )

    assert failure is None
