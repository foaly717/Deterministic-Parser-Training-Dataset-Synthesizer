from pathlib import Path

from dataset_tools.parsers.man_models import ManEntry
from dataset_tools.parsers.man_page import parse_man_page


FIXTURE = Path("data/evidence/sample-man-page.txt")


def test_parser_returns_man_entries():
    entries = parse_man_page(FIXTURE)

    assert isinstance(entries, list)
    assert all(isinstance(entry, ManEntry) for entry in entries)

def test_parser_preserves_sections_and_provenance():
    entries = parse_man_page(FIXTURE)

    name = next(entry for entry in entries if entry.name == "NAME")

    assert name.section == "NAME"
    assert name.source_sha256
    assert name.line_start == 2
    assert name.description
