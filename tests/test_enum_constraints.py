from dataset_tools.evidence.constraints import EnumConstraint


def test_enum_constraint_preserves_documented_value():
    constraint = EnumConstraint(
        name="handbrake-preset",
        category="cli_constraint",
        subject="--preset",
        allowed_values=["Fast", "HQ 1080p30 Surround"],
        metadata={"source_id": "handbrakecli-help"},
    )

    assert "Fast" in constraint.allowed_values


def test_enum_constraint_rejects_fabricated_value():
    constraint = EnumConstraint(
        name="handbrake-preset",
        category="cli_constraint",
        subject="--preset",
        allowed_values=["Fast", "HQ 1080p30 Surround"],
        metadata={"source_id": "handbrakecli-help"},
    )

    assert "High Profile" not in constraint.allowed_values


def test_enum_constraint_preserves_provenance():
    constraint = EnumConstraint(
        name="handbrake-preset",
        category="cli_constraint",
        subject="--preset",
        allowed_values=["Fast"],
        metadata={
            "source_id": "handbrakecli-help",
            "source_sha256": "a" * 64,
        },
    )

    assert constraint.metadata["source_id"] == "handbrakecli-help"
    assert len(constraint.metadata["source_sha256"]) == 64
