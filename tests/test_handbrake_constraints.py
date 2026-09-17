import pytest
from dataset_tools.validators.constraints import validate_constraints


def test_documented_preset_is_accepted():
    constraints = {"--preset": {"Very Fast 1080p30", "HQ 1080p30 Surround"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Very Fast 1080p30"'
    
    ok, message = validate_constraints(response, constraints)
    assert ok is True


def test_fabricated_preset_is_rejected():
    constraints = {"--preset": {"Very Fast 1080p30", "HQ 1080p30 Surround"}}
    response = 'HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Nonexistent Preset"'
    
    ok, message = validate_constraints(response, constraints)
    assert ok is False
    assert "Unsupported value for --preset: Nonexistent Preset" in message
