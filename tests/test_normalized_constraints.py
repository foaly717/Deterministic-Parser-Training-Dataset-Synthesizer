from dataset_tools.evidence.constraints import EnumConstraint
from dataset_tools.evidence.schema import (
    EvidenceSource,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)


def test_normalized_fact_can_store_constraints():
    fact = NormalizedEvidenceFact(
        category="constraint",
        subject="ExampleCLI",
        predicate="allowed_value",
        value="alpha",
        metadata={
            "applies_to": "--mode",
            "source_id": "example-help",
        },
    )

    assert fact.category == "constraint"
    assert fact.metadata["applies_to"] == "--mode"


def test_constraint_is_not_parser_specific():
    fact = NormalizedEvidenceFact(
        category="constraint",
        subject="ExampleTool",
        predicate="allowed_value",
        value="inner",
        metadata={
            "applies_to": "JOIN",
        },
    )

    assert fact.value == "inner"


def test_normalized_document_stores_constraints_as_canonical_objects():
    constraint = EnumConstraint(
        name="example-mode",
        category="cli_constraint",
        subject="--mode",
        allowed_values=["alpha"],
        metadata={"source_id": "example-help"},
    )

    document = NormalizedEvidenceDocument(
        source=EvidenceSource(
            source_id="example-help",
            path="example.txt",
            source_type="text",
            sha256="abc",
        ),
        facts=[],
        constraints=[constraint],
    )

    assert document.constraints[0].name == "example-mode"
    assert document.constraints[0].metadata["source_id"] == "example-help"
