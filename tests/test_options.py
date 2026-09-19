from dataset_tools.validators.options import validate_cli_response


VALID_OPTIONS = frozenset({
    "--preset-import-file",
    "--preset-export",
    "--preset-export-description",
    "--preset-export-file",
    "-Z",
})


def test_supported_long_option_is_accepted():
    ok, message = validate_cli_response(
        "HandBrakeCLI --preset-import-file my_presets.json",
        VALID_OPTIONS,
    )

    assert ok is True
    assert "supported" in message.lower()


def test_unsupported_option_is_rejected():
    ok, message = validate_cli_response(
        "HandBrakeCLI --not-a-real-option input.mkv",
        VALID_OPTIONS,
    )

    assert ok is False
    assert "--not-a-real-option" in message


def test_executable_suffix_is_not_treated_as_option():
    ok, message = validate_cli_response(
        "ffmpeg-cli --preset-export MyPreset",
        VALID_OPTIONS,
    )

    assert ok is True
    assert "-cli" not in message


def test_tool_executable_suffix_is_not_treated_as_option():
    ok, message = validate_cli_response(
        "preset-tool --preset-import-file my_presets.json",
        VALID_OPTIONS,
    )

    assert ok is True
    assert "-tool" not in message
