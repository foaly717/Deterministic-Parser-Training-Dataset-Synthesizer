from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.loaders.text import TextEvidenceLoader


def test_text_loader_supports_text_files():
    loader = TextEvidenceLoader()
    assert loader.supports(Path("example.txt"))
    assert loader.supports(Path("example.md"))
    assert not loader.supports(Path("example.json"))


def test_text_loader_creates_normalized_document(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("alpha\nbeta\n", encoding="utf-8")

    document = load_evidence(source)

    assert document.source.source_type == "text"
    assert document.source.sha256
    assert len(document.facts) == 2
    assert document.facts[0].value == "alpha"

from dataset_tools.evidence.registry import load_evidence


def test_loaded_document_populates_constraints(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("plain evidence\\n", encoding="utf-8")

    document = load_evidence(source)

    assert document.constraints == []
