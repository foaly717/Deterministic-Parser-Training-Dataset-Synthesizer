from dataset_tools.parsers.cli_parser import parse_cli_command
from dataset_tools.validators.options import validate_options


def test_alias_option_is_accepted():
    valid_options = frozenset({
        "-help",
        "-h",
        "-?",
        "--help",
    })

    ok_h, _ = validate_options(
        parse_cli_command(
        "ffmpeg -h",
        ),
        valid_options,
    )
    ok_help, _ = validate_options(
        parse_cli_command(
        "ffmpeg --help",
        ),
        valid_options,
    )
    ok_q, _ = validate_options(
        parse_cli_command(
        "ffmpeg -?",
        ),
        valid_options,
    )

    assert ok_h is True
    assert ok_help is True
    assert ok_q is True
