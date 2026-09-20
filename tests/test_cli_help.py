from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import SemanticPredicate


HELP = Path("data/evidence/handbrakecli-help.txt")


def test_cli_help_produces_canonical_support_facts():
    document = load_evidence(HELP)

    options = {
        fact.value
        for fact in document.facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    }

    assert "--preset" in options
    assert "--audio" in options
    assert "--vfr" in options
    assert "--cfr" in options
    assert "--pfr" in options


def test_cli_help_preserves_declaration_provenance():
    document = load_evidence(HELP)

    preset = next(
        fact
        for fact in document.facts
        if (
            fact.predicate is SemanticPredicate.SUPPORTS
            and fact.value == "--preset"
        )
    )

    assert preset.subject == "HandBrakeCLI"
    assert preset.provenance.line_start == 10
    assert preset.provenance.line_end == 12
    assert preset.provenance.section == "General Options"
    assert preset.provenance.raw_snippet


def test_cli_help_does_not_treat_preset_example_as_enum():
    document = load_evidence(HELP)

    values = {
        fact.value
        for fact in document.facts
        if (
            fact.predicate is SemanticPredicate.ENUMERATES
            and fact.subject == "--preset"
        )
    }

    assert values == set()


def test_cli_help_extracts_documented_enumerations():
    document = load_evidence(HELP)

    values = {
        fact.value
        for fact in document.facts
        if (
            fact.predicate is SemanticPredicate.ENUMERATES
            and fact.subject == "--format"
        )
    }

    assert values == {"av_mp4", "av_mkv", "av_webm"}


def test_cli_help_extracts_handbrake_enum_facts():
    document = load_evidence(HELP)

    enum_facts = [
        fact
        for fact in document.facts
        if fact.predicate is SemanticPredicate.ENUMERATES
    ]

    assert len(enum_facts) == 102


def test_cli_help_preserves_generic_extractor_contract():
    from dataset_tools.evidence.loaders.cli_help import (
        extract_cli_option_facts,
    )

    sample_help = """Usage: tool [-v]

  -h      show help
  -r      raw output
"""

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_test_123",
        subject="tool",
    )

    assert len(facts) == 3
    assert [fact.value for fact in facts] == ["-v", "-h", "-r"]
    assert facts[0].provenance.line_start == 1
    assert facts[0].provenance.line_end == 1
    assert facts[0].provenance.raw_snippet == "Usage: tool [-v]"
    assert facts[1].provenance.line_start == 3
    assert facts[2].provenance.line_start == 4
