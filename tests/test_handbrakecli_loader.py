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
