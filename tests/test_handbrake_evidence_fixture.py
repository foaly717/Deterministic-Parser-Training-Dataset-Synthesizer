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


def test_handbrake_evidence_fixture_does_not_invent_preset_values():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    cli_options = {
        fact.value
        for fact in document.facts
        if fact.category == "cli_option"
    }

    assert "--preset" in cli_options
    assert "--preset-list" in cli_options

    preset_constraints = [
        constraint
        for constraint in document.constraints
        if constraint.name == "--preset"
    ]

    assert preset_constraints == []
