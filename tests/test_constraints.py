import pytest
from dataset_tools.validators.constraints import validate_constraints


def test_documented_enum_value_is_accepted():
    constraints = {"--encoder": {"x264", "x265", "vt_h264"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --encoder "x264"'
    
    ok, message = validate_constraints(response, constraints)
    assert ok is True
    assert "satisfied" in message


def test_fabricated_enum_value_is_rejected():
    constraints = {"--encoder": {"x264", "x265", "vt_h264"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --encoder "invalid_codec"'
    
    ok, message = validate_constraints(response, constraints)
    assert ok is False
    assert "Unsupported value for --encoder: invalid_codec" in message
