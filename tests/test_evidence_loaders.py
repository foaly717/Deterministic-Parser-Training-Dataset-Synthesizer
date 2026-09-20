from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat


def test_loaded_markdown_document_is_canonical(tmp_path):
    source = tmp_path / "sample.md"

    source.write_text(
        "# Evidence\n\nplain evidence\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.metadata.format is DocumentFormat.MARKDOWN
    assert document.facts == []
    assert extract_constraints(document) == []
