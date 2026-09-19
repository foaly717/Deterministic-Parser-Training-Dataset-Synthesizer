from dataset_tools.parsers.cli_parser import parse_cli_command
from dataset_tools.validators.options import validate_options


VALID_OPTIONS = frozenset(
    {
        "--preset-import-file",
        "--preset-export",
        "--preset-export-description",
    }
)


def test_validate_options_accepts_parsed_command():
    command = parse_cli_command(
        "HandBrakeCLI --preset-export Example"
    )

    ok, message = validate_options(
        command,
        VALID_OPTIONS,
    )

    assert ok is True
    assert "supported" in message.lower()


def test_validate_options_rejects_unknown_parsed_option():
    command = parse_cli_command(
        "HandBrakeCLI --does-not-exist value"
    )

    ok, message = validate_options(
        command,
        VALID_OPTIONS,
    )

    assert ok is False
    assert "--does-not-exist" in message
