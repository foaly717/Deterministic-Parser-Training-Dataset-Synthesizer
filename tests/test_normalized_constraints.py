from dataset_tools.evidence.schema import (
    EnumConstraint,
    TypeConstraint,
)


def test_enum_constraint_requires_values():
    constraint = EnumConstraint(
        constraint_id="test-enum",
        target_entity="--mode",
        source_fact_ids=["fact-a", "fact-b"],
        allowed_values=["alpha", "beta"],
    )

    assert constraint.constraint_type == "enum"
    assert constraint.target_entity == "--mode"
    assert sorted(constraint.allowed_values) == [
        "alpha",
        "beta",
    ]
    assert constraint.source_fact_ids == [
        "fact-a",
        "fact-b",
    ]


def test_type_constraint_preserves_source_lineage():
    constraint = TypeConstraint(
        constraint_id="test-type",
        target_entity="--preset",
        source_fact_ids=["fact-preset"],
        expected_type="str",
    )

    assert constraint.constraint_type == "type"
    assert constraint.target_entity == "--preset"
    assert constraint.expected_type == "str"
    assert constraint.source_fact_ids == [
        "fact-preset",
    ]
