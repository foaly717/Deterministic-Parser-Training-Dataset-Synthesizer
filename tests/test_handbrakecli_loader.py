from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat, SemanticPredicate


def test_handbrakecli_loader_produces_cli_facts():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.artifact.source_id == "handbrakecli-help"
    assert document.metadata.format is DocumentFormat.CLI_HELP
    assert document.metadata.tool is not None
    assert document.metadata.tool.name == "HandBrakeCLI"

    options = {
        fact.value
        for fact in document.facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    }

    assert "--preset" in options
    assert "--help" in options

    preset = next(
        fact
        for fact in document.facts
        if (
            fact.predicate is SemanticPredicate.SUPPORTS
            and fact.value == "--preset"
        )
    )

    assert preset.subject == "HandBrakeCLI"
    assert preset.provenance.line_start
    assert preset.provenance.section == "General Options"
