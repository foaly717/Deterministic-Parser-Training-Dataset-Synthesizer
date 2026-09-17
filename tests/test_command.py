from dataset_tools.validators.command import validate_cli_command


def test_expected_executable_is_accepted():
    ok, message = validate_cli_command(
        "HandBrakeCLI --preset-export MyPreset",
        "HandBrakeCLI",
    )

    assert ok is True
    assert "expected executable" in message.lower()


def test_invented_executable_is_rejected():
    ok, message = validate_cli_command(
        "preset-tool --preset-import-file my_presets.json",
        "HandBrakeCLI",
    )

    assert ok is False
    assert "preset-tool" in message


def test_ffmpeg_substitution_is_rejected():
    ok, message = validate_cli_command(
        "ffmpeg-cli --preset-export MyPreset",
        "HandBrakeCLI",
    )

    assert ok is False
    assert "ffmpeg-cli" in message


def test_prose_before_command_is_rejected():
    ok, message = validate_cli_command(
        "Run this command: HandBrakeCLI --preset-export MyPreset",
        "HandBrakeCLI",
    )

    assert ok is False


def test_multiple_lines_are_rejected():
    ok, message = validate_cli_command(
        "HandBrakeCLI --preset-export MyPreset\n"
        "Then verify the output.",
        "HandBrakeCLI",
    )

    assert ok is False
