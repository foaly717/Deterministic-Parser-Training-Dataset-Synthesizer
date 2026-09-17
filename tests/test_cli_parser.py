from pathlib import Path

from dataset_tools.parsers.cli_help import parse_cli_help


def test_cli_parser_preserves_option_metadata():
    options = parse_cli_help(Path("data/evidence/handbrakecli-help.txt"))

    preset = next(
        option
        for option in options
        if option.name == "--preset"
    )

    assert preset.argument == "<string>"
    assert preset.aliases == ["-Z"]
    assert preset.section == "General Options"
    assert preset.description
