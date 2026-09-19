from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.validators.options import validate_cli_response


def test_equals_syntax_option_validation():
    valid_options = frozenset({
        "ExampleCLI",
        "--mode",
        "-i",
        "-o",
    })

    ok, msg = validate_cli_response(
        'ExampleCLI --mode="alpha"',
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
