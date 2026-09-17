from dataset_tools.constraints.models import EnumConstraint


def test_enum_constraint_preserves_documented_value():
    constraint = EnumConstraint(
        option="--preset",
        values=["Fast", "HQ 1080p30 Surround"],
        source_id="handbrakecli-help",
        source_sha256="a" * 64,
    )

    assert "Fast" in constraint.values


def test_enum_constraint_rejects_fabricated_value():
    constraint = EnumConstraint(
        option="--preset",
        values=["Fast", "HQ 1080p30 Surround"],
        source_id="handbrakecli-help",
        source_sha256="a" * 64,
    )

    assert "High Profile" not in constraint.values


def test_enum_constraint_preserves_provenance():
    constraint = EnumConstraint(
        option="--preset",
        values=["Fast"],
        source_id="handbrakecli-help",
        source_sha256="a" * 64,
    )

    assert constraint.source_id == "handbrakecli-help"
    assert len(constraint.source_sha256) == 64
