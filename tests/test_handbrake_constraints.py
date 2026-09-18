from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.validators.reason_codes import ValidationReasonCode


def test_documented_preset_is_accepted():
    constraints = {"--preset": {"Very Fast 1080p30", "HQ 1080p30 Surround"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Very Fast 1080p30"'

    failure = validate_constraints(response, constraints)
    assert failure is None


def test_fabricated_preset_is_rejected():
    constraints = {"--preset": {"Very Fast 1080p30", "HQ 1080p30 Surround"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Nonexistent Preset"'

    failure = validate_constraints(response, constraints)
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.UNSUPPORTED_ENUM_VALUE
