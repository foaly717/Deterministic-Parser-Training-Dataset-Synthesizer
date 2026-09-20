from pathlib import Path

import pytest

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat


def test_registry_selects_markdown_loader(tmp_path):
    source = tmp_path / "README.md"

    source.write_text(
        "# Project\n\nDocumentation\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.metadata.format is DocumentFormat.MARKDOWN


def test_registry_rejects_generic_text_file(tmp_path):
    source = tmp_path / "notes.txt"

    source.write_text(
        "Plain text evidence\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No evidence loader available"):
        load_evidence(source)


def test_registry_rejects_unknown_extension(tmp_path):
    source = tmp_path / "evidence.xyz"

    source.write_text(
        "Unknown format\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No evidence loader available"):
        load_evidence(source)
