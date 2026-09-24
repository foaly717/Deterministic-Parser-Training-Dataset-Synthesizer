from pathlib import Path

from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import DocumentFormat, EnumConstraint, SemanticPredicate


def test_handbrake_evidence_fixture_loads():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.artifact.source_id == "handbrakecli-help"
    assert document.artifact.source_sha256
    assert document.metadata.format is DocumentFormat.CLI_HELP
    assert document.metadata.tool is not None
    assert document.metadata.tool.name == "HandBrakeCLI"
    assert len(document.facts) > 0

    cli_options = {
        fact.value
        for fact in document.facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    }

    assert "--preset" in cli_options


def test_handbrake_evidence_fixture_does_not_invent_preset_values():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    cli_options = {
        fact.value
        for fact in document.facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    }

    assert "--preset" in cli_options
    assert "--preset-list" in cli_options

    preset_constraints = [
        constraint
        for constraint in extract_constraints(document)
        if constraint.target_entity == "--preset"
    ]

    assert all(
        not isinstance(constraint, EnumConstraint)
        for constraint in preset_constraints
    )
