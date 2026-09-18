from dataset_tools.evidence.constraints import EnumConstraint


def test_enum_constraint_preserves_documented_value():
    constraint = EnumConstraint(
        name="example-mode",
        category="cli_constraint",
        subject="--mode",
        allowed_values=["alpha", "beta"],
        metadata={"source_id": "example-help"},
    )

    assert "alpha" in constraint.allowed_values


def test_enum_constraint_rejects_fabricated_value():
    constraint = EnumConstraint(
        name="example-mode",
        category="cli_constraint",
        subject="--mode",
        allowed_values=["alpha", "beta"],
        metadata={"source_id": "example-help"},
    )

    assert "gamma" not in constraint.allowed_values


def test_enum_constraint_preserves_provenance():
    constraint = EnumConstraint(
        name="example-mode",
        category="cli_constraint",
        subject="--mode",
        allowed_values=["alpha"],
        metadata={
            "source_id": "example-help",
            "source_sha256": "a" * 64,
        },
    )

    assert constraint.metadata["source_id"] == "example-help"
    assert len(constraint.metadata["source_sha256"]) == 64
