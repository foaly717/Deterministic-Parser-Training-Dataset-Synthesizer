from pathlib import Path

from dataset_tools.evidence.registry import load_evidence


def test_handbrake_evidence_fixture_loads():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.source.source_id == "handbrakecli-help"
    assert document.source.source_type == "handbrakecli"
    assert document.source.sha256
    assert len(document.facts) > 0

    cli_options = {
        fact.value
        for fact in document.facts
        if fact.category == "cli_option"
    }

    assert "--preset" in cli_options


def test_handbrake_evidence_fixture_populates_constraints():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.constraints

    preset_constraint = next(
        constraint
        for constraint in document.constraints
        if constraint.name == "--preset"
    )

    assert preset_constraint.allowed_values
    assert preset_constraint.metadata["source_id"] == "handbrakecli-help"
