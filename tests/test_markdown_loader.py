from dataset_tools.evidence.registry import load_evidence


def test_markdown_loader_selected(tmp_path):
    source = tmp_path / "README.md"

    source.write_text(
        "# Title\n\nExample text\n",
        encoding="utf-8",
    )

    document = load_evidence(source)

    assert document.source_type == "markdown"
    assert document.source_sha256
    assert len(document.facts) == 2
    assert document.facts[0].category == "markdown"
