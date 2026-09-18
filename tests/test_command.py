from dataset_tools.validators.command import validate_cli_command
from dataset_tools.validators.reason_codes import ValidationReasonCode


def test_expected_executable_is_accepted():
    failure = validate_cli_command(
        "HandBrakeCLI --preset-export MyPreset",
        "HandBrakeCLI",
    )
    assert failure is None


def test_invented_executable_is_rejected():
    failure = validate_cli_command(
        "preset-tool --preset-import-file my_presets.json",
        "HandBrakeCLI",
    )
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.UNEXPECTED_EXECUTABLE


def test_ffmpeg_substitution_is_rejected():
    failure = validate_cli_command(
        "ffmpeg-cli --preset-export MyPreset",
        "HandBrakeCLI",
    )
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.UNEXPECTED_EXECUTABLE


def test_prose_before_command_is_rejected():
    failure = validate_cli_command(
        "Run this command: HandBrakeCLI --preset-export MyPreset",
        "HandBrakeCLI",
    )
    assert failure is not None


def test_multiple_lines_are_rejected():
    failure = validate_cli_command(
        "HandBrakeCLI --preset-export MyPreset\n"
        "Then verify the output.",
        "HandBrakeCLI",
    )
    assert failure is not None
    assert failure.reason_code == ValidationReasonCode.INVALID_STRUCTURE
