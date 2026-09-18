from dataset_tools.validators.constraints import validate_constraints
from dataset_tools.validators.reason_codes import ValidationReasonCode


def test_documented_enum_value_is_accepted():
    constraints = {"--encoder": {"x264", "x265", "vt_h264"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --encoder "x264"'

    failure = validate_constraints(response, constraints)
    assert failure is None


def test_fabricated_enum_value_is_rejected():
    constraints = {"--encoder": {"x264", "x265", "vt_h264"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --encoder "invalid_codec"'

    failure = validate_constraints(response, constraints)
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.UNSUPPORTED_ENUM_VALUE
