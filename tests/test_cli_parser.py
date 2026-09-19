import pytest

from dataset_tools.parsers.cli_parser import (
    CLIParseError,
    parse_cli_command,
)


def test_parser_handles_flag_value():
    command = parse_cli_command(
        "HandBrakeCLI --preset VeryFast"
    )

    assert command.executable == "HandBrakeCLI"
    assert command.options[0].name == "--preset"
    assert command.options[0].value == "VeryFast"


def test_parser_handles_equals_syntax():
    command = parse_cli_command(
        "HandBrakeCLI --preset=VeryFast"
    )

    assert command.options[0].name == "--preset"
    assert command.options[0].value == "VeryFast"


def test_parser_handles_boolean_flag():
    command = parse_cli_command(
        "HandBrakeCLI --verbose"
    )

    assert command.options[0].name == "--verbose"
    assert command.options[0].value is None


def test_parser_rejects_empty_command():
    with pytest.raises(CLIParseError):
        parse_cli_command("")


def test_cli_parser_rejects_multiple_commands():
    from dataset_tools.parsers.cli_parser import CLIParseError

    try:
        parse_cli_command(
            "HandBrakeCLI --preset-export MyPreset\n"
            "Then verify the output."
        )
    except CLIParseError:
        return

    assert False, "Expected CLIParseError for multiline command"
