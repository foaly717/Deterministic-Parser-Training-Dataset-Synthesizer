from dataset_tools.evidence.index import EvidenceIndex
from dataset_tools.validators.options import validate_cli_response
from dataset_tools.validators.constraints import validate_constraints


def test_equals_syntax_option_validation():
    valid_options = {"HandBrakeCLI", "--preset", "-i", "-o"}
    evidence_index = EvidenceIndex(valid_options=valid_options)

    ok, msg = validate_cli_response('HandBrakeCLI --preset="Fast 1080p30"', evidence_index)
    assert ok is True


def test_equals_syntax_constraint_validation():
    constraints = {"--preset": {"Fast 1080p30", "HQ 1080p30"}}

    failure = validate_constraints('HandBrakeCLI --preset="Fast 1080p30"', constraints)
    assert failure is None
