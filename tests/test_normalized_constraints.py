from dataset_tools.evidence.schema import NormalizedEvidenceFact


def test_normalized_fact_can_store_constraints():
    fact = NormalizedEvidenceFact(
        category="constraint",
        subject="HandBrakeCLI",
        predicate="allowed_value",
        value="Fast",
        metadata={
            "applies_to": "--preset",
            "source_id": "handbrakecli-help",
        },
    )

    assert fact.category == "constraint"
    assert fact.metadata["applies_to"] == "--preset"


def test_constraint_is_not_parser_specific():
    fact = NormalizedEvidenceFact(
        category="constraint",
        subject="PostgreSQL",
        predicate="allowed_value",
        value="inner",
        metadata={
            "applies_to": "JOIN",
        },
    )

    assert fact.value == "inner"

from dataset_tools.evidence.constraints import EnumConstraint
from dataset_tools.evidence.schema import EvidenceSource, NormalizedEvidenceDocument


def test_normalized_document_stores_constraints_as_canonical_objects():
    constraint = EnumConstraint(
        name="handbrake-preset",
        category="cli_constraint",
        subject="--preset",
        allowed_values=["Fast 1080p30"],
        metadata={"source_id": "handbrake-help"},
    )

    document = NormalizedEvidenceDocument(
        source=EvidenceSource(
            source_id="handbrake-help",
            path="handbrake.txt",
            source_type="text",
            sha256="abc",
        ),
        facts=[],
        constraints=[constraint],
    )

    assert document.constraints[0].name == "handbrake-preset"
    assert document.constraints[0].metadata["source_id"] == "handbrake-help"
