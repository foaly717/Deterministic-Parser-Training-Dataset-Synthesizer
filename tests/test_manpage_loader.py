from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat


FIXTURE = Path("data/evidence/sample-man-page.txt")


def test_man_page_loader_produces_canonical_document():
    document = load_evidence(FIXTURE)

    assert document.artifact.source_id == "sample-man-page"
    assert len(document.artifact.source_sha256) == 64
    assert document.metadata.format is DocumentFormat.MAN_PAGE
    assert document.metadata.tool is not None
    assert document.metadata.tool.name == "sample-man-page"
    assert document.metadata.role == "MANUAL"
    assert document.facts == []
