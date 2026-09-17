from pathlib import Path

from dataset_tools.evidence.registry import load_evidence


def test_handbrakecli_loader_produces_cli_facts():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.source.source_type == "handbrakecli"

    options = {
        fact.value
        for fact in document.facts
        if fact.category == "cli_option"
    }

    assert "--preset" in options
    assert "--help" in options

    preset = next(
        fact
        for fact in document.facts
        if fact.value == "--preset"
    )

    assert preset.metadata["argument"] == "<string>"
    assert preset.metadata["description"]
    assert "-Z" in preset.metadata["aliases"]
    assert preset.metadata["source_line_start"]
    assert preset.metadata["section"]
    preset = next(
        fact
        for fact in document.facts
        if fact.value == "--preset"
    )

    assert preset.metadata["section"] == "General Options"
    assert preset.metadata["argument"] == "<string>"
    assert preset.metadata["description"]
    assert preset.metadata["source_line_start"]
