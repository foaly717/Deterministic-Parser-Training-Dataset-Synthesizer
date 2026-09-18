from dataset_tools.evidence.index import EvidenceIndex
from dataset_tools.validators.options import validate_cli_response
from dataset_tools.validators.constraints import validate_constraints


def test_equals_syntax_option_validation():
    valid_options = {"ExampleCLI", "--mode", "-i", "-o"}
    evidence_index = EvidenceIndex(valid_options=valid_options)

    ok, msg = validate_cli_response(
        'ExampleCLI --mode="alpha"',
        evidence_index,
    )
    assert ok is True


def test_equals_syntax_constraint_validation():
    constraints = {"--mode": {"alpha", "beta"}}

    failure = validate_constraints(
        'ExampleCLI --mode="alpha"',
        constraints,
    )
    assert failure is None
