from pathlib import Path

import pytest

from dataset_tools.evidence.registry import load_evidence


def test_registry_selects_markdown_loader(tmp_path):
    source = tmp_path / "README.md"

    source.write_text(
        "# Project\n\nDocumentation\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.source_type == "markdown"


def test_registry_selects_text_loader(tmp_path):
    source = tmp_path / "notes.txt"

    source.write_text(
        "Plain text evidence\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.source_type == "text"


def test_registry_rejects_unknown_extension(tmp_path):
    source = tmp_path / "evidence.xyz"

    source.write_text(
        "Unknown format\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No evidence loader available"):
        load_evidence(source)
