from types import SimpleNamespace

from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.schema import NormalizedEvidenceFact


def test_extract_constraints_uses_allowed_values_from_evidence_fact():
    fact = NormalizedEvidenceFact(
        category="cli_constraint",
        subject="--mode",
        predicate="allows",
        value="alpha",
        extraction_type="enum",
        metadata={
            "allowed_values": ["alpha", "beta"],
            "source_id": "example-help",
        },
    )
    document = SimpleNamespace(
        source=SimpleNamespace(source_id="example-help"),
        facts=[fact],
    )

    constraints = extract_constraints(document)

    assert len(constraints) == 1
    assert constraints[0].subject == "--mode"
    assert constraints[0].allowed_values == ["alpha", "beta"]
    assert constraints[0].metadata["source_id"] == "example-help"


def test_extract_constraints_does_not_invent_values_for_non_enum_facts():
    fact = NormalizedEvidenceFact(
        category="cli_option",
        subject="ExampleCLI",
        predicate="supports",
        value="--mode",
        extraction_type=None,
        metadata={},
    )
    document = SimpleNamespace(
        source=SimpleNamespace(source_id="example-help"),
        facts=[fact],
    )

    constraints = extract_constraints(document)

    assert constraints == []
