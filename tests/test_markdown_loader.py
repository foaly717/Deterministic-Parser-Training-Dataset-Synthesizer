from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat


def test_markdown_loader_selected(tmp_path):
    source = tmp_path / "README.md"

    source.write_text(
        "# Title\n\nExample text\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.artifact.source_id == "README"
    assert document.artifact.source_sha256
    assert document.metadata.format is DocumentFormat.MARKDOWN
    assert document.metadata.tool is None
    assert document.facts == []
