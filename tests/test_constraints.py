from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.validators.reason_codes import ValidationReasonCode


def test_documented_enum_value_is_accepted():
    constraints = {"--mode": {"alpha", "beta", "delta"}}
    response = 'ExampleCLI --mode "alpha"'

    failure = validate_constraints(response, constraints)
    assert failure is None


def test_fabricated_enum_value_is_rejected():
    constraints = {"--mode": {"alpha", "beta", "delta"}}
    response = 'ExampleCLI --mode "gamma"'

    failure = validate_constraints(response, constraints)
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.UNSUPPORTED_ENUM_VALUE
