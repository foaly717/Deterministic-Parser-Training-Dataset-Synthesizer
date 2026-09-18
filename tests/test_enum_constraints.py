from dataset_tools.evidence.schema import EnumConstraint


def test_enum_constraint_preserves_documented_value():
    constraint = EnumConstraint(
        constraint_id="constraint-example-mode",
        target_entity="--mode",
        source_fact_ids=["fact-alpha", "fact-beta"],
        allowed_values=["alpha", "beta"],
    )

    assert "alpha" in constraint.allowed_values


def test_enum_constraint_rejects_fabricated_value():
    constraint = EnumConstraint(
        constraint_id="constraint-example-mode",
        target_entity="--mode",
        source_fact_ids=["fact-alpha", "fact-beta"],
        allowed_values=["alpha", "beta"],
    )

    assert "gamma" not in constraint.allowed_values


def test_enum_constraint_preserves_provenance():
    constraint = EnumConstraint(
        constraint_id="constraint-example-mode",
        target_entity="--mode",
        source_fact_ids=["fact-alpha"],
        allowed_values=["alpha"],
    )

    assert constraint.target_entity == "--mode"
    assert constraint.source_fact_ids == ["fact-alpha"]
