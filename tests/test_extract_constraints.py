from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    EnumConstraint,
    FactCategory,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
    TypeConstraint,
)


def _make_provenance(source_id: str, source_sha256: str, line: int, snippet: str) -> Provenance:
    """Helper to generate standard test provenance objects."""
    return Provenance(
        source_id=source_id,
        source_sha256=source_sha256,
        line_start=line,
        line_end=line,
        section="Options",
        raw_snippet=snippet,
    )


def test_extract_enum_constraint_from_facts():
    source_id = "handbrake_cli_help"
    source_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    doc_id = document_id(source_id, source_sha256)

    prov_alpha = _make_provenance(
        source_id,
        source_sha256,
        42,
        "--mode <alpha|beta>",
    )
    prov_beta = _make_provenance(
        source_id,
        source_sha256,
        43,
        "--mode <alpha|beta>",
    )

    fact_alpha = NormalizedEvidenceFact(
        fact_id=fact_id(
            doc_id,
            "ENUM_VALUE",
            "--mode",
            "enumerates",
            "alpha",
            prov_alpha.model_dump(),
        ),
        document_id=doc_id,
        category=FactCategory.ENUM_VALUE,
        subject="--mode",
        predicate="enumerates",
        value="alpha",
        provenance=prov_alpha,
    )

    fact_beta = NormalizedEvidenceFact(
        fact_id=fact_id(
            doc_id,
            "ENUM_VALUE",
            "--mode",
            "enumerates",
            "beta",
            prov_beta.model_dump(),
        ),
        document_id=doc_id,
        category=FactCategory.ENUM_VALUE,
        subject="--mode",
        predicate="enumerates",
        value="beta",
        provenance=prov_beta,
    )

    document = NormalizedEvidenceDocument(
        document_id=doc_id,
        source_id=source_id,
        source_type="cli_help",
        source_sha256=source_sha256,
        facts=[fact_alpha, fact_beta],
    )

    constraints = extract_constraints(document)

    mode_constraints = [
        c for c in constraints
        if c.target_entity == "--mode"
    ]

    assert len(mode_constraints) == 1

    mode_constraint = mode_constraints[0]

    assert isinstance(mode_constraint, EnumConstraint)
    assert mode_constraint.target_entity == "--mode"
    assert mode_constraint.allowed_values
    assert len(mode_constraint.allowed_values) >= 1
    assert sorted(mode_constraint.allowed_values) == ["alpha", "beta"]

    expected_fact_ids = sorted(
        [fact_alpha.fact_id, fact_beta.fact_id]
    )

    assert sorted(mode_constraint.source_fact_ids) == expected_fact_ids

    fact_index = {
        fact.fact_id: fact
        for fact in document.facts
    }

    for f_id in mode_constraint.source_fact_ids:
        fact = fact_index[f_id]
        assert fact.provenance.source_id == source_id
        assert fact.provenance.source_sha256 == source_sha256


def test_unenumerated_string_compiles_to_type_constraint():
    source_id = "handbrake_cli_help"
    source_sha256 = "0" * 64
    doc_id = document_id(source_id, source_sha256)

    prov = _make_provenance(
        source_id,
        source_sha256,
        10,
        "--preset <string>",
    )

    preset_fact = NormalizedEvidenceFact(
        fact_id=fact_id(
            doc_id,
            "CLI_OPTION",
            "--preset",
            "accepts_type",
            "string",
            prov.model_dump(),
        ),
        document_id=doc_id,
        category=FactCategory.CLI_OPTION,
        subject="--preset",
        predicate="accepts_type",
        value="string",
        provenance=prov,
    )

    document = NormalizedEvidenceDocument(
        document_id=doc_id,
        source_id=source_id,
        source_type="cli_help",
        source_sha256=source_sha256,
        facts=[preset_fact],
    )

    constraints = extract_constraints(document)

    assert len(constraints) == 1

    preset_constraint = constraints[0]

    assert isinstance(preset_constraint, TypeConstraint)
    assert preset_constraint.constraint_type == "type"
    assert preset_constraint.target_entity == "--preset"
    assert preset_constraint.expected_type == "str"
    assert preset_constraint.source_fact_ids == [preset_fact.fact_id]

    assert not any(
        isinstance(c, EnumConstraint)
        for c in constraints
    )
