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
