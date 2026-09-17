from pathlib import Path

from dataset_tools.parsers.cli_help import parse_cli_help
from dataset_tools.parsers.cli_models import CLIOption


HELP = Path("data/evidence/handbrakecli-help.txt")


def get_option(name: str) -> CLIOption:
    options = parse_cli_help(HELP)
    return next(option for option in options if option.name == name)


def test_parser_returns_clioption_models():
    options = parse_cli_help(HELP)

    assert options
    assert all(isinstance(option, CLIOption) for option in options)


def test_clioption_preserves_flag_metadata():
    option = get_option("--preset")

    assert option.name == "--preset"
    assert option.aliases == ["-Z"]
    assert option.argument == "<string>"
    assert option.section == "General Options"


def test_clioption_preserves_source_provenance():
    option = get_option("--preset")

    assert option.source_id
    assert option.source_sha256
    assert option.line_start == 10
    assert option.line_end == 12


def test_clioption_has_no_normalized_evidence_fields():
    option = get_option("--preset")

    assert not hasattr(option, "kind")
    assert not hasattr(option, "predicate")
    assert not hasattr(option, "metadata")
