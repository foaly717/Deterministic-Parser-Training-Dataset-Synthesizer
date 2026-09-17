from pathlib import Path

from dataset_tools.parsers.man_page import parse_man_page
from dataset_tools.parsers.man_models import ManEntry


FIXTURE = Path("data/evidence/sample-man-page.txt")


def test_parser_returns_manentry_models():
    entries = parse_man_page(FIXTURE)

    assert entries
    assert all(isinstance(entry, ManEntry) for entry in entries)


def test_manentry_preserves_section():
    entries = parse_man_page(FIXTURE)
    entry = next(entry for entry in entries if entry.name == "NAME")

    assert entry.section == "NAME"


def test_manentry_normalizes_dash_escape():
    entries = parse_man_page(FIXTURE)
    entry = next(entry for entry in entries if entry.description)

    assert "-" in entry.description
    assert "\\\\-" not in entry.description


def test_manentry_preserves_source_hash():
    entry = parse_man_page(FIXTURE)[0]

    assert len(entry.source_sha256) == 64
