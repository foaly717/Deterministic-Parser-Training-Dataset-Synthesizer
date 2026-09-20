from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.ids import compute_document_id, compute_fact_id
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    EnumConstraint,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
    SemanticPredicate,
    ToolIdentity,
    TypeConstraint,
)


def _make_provenance(line: int, snippet: str) -> Provenance:
    return Provenance(
        line_start=line,
        line_end=line,
        section="Options",
        raw_snippet=snippet,
    )


def _document(*, source_id, source_sha256, facts):
    document_id = compute_document_id(source_id, source_sha256)
    assert all(fact.document_id == document_id for fact in facts)

    return NormalizedEvidenceDocument(
        document_id=document_id,
        artifact=ArtifactIdentity(
            source_id=source_id,
            source_sha256=source_sha256,
        ),
        metadata=DocumentMetadata(
            format=DocumentFormat.CLI_HELP,
            tool=ToolIdentity(name="HandBrakeCLI"),
        ),
        facts=facts,
    )


def test_extract_enum_constraint_from_facts():
    source_id = "handbrake_cli_help"
    source_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    doc_id = compute_document_id(source_id, source_sha256)

    prov_alpha = _make_provenance(42, "--mode <alpha|beta>")
    prov_beta = _make_provenance(43, "--mode <alpha|beta>")

    fact_alpha = NormalizedEvidenceFact(
        fact_id=compute_fact_id(
            doc_id, "--mode", SemanticPredicate.ENUMERATES.value,
            "alpha", prov_alpha.model_dump(),
        ),
        document_id=doc_id,
        subject="--mode",
        predicate=SemanticPredicate.ENUMERATES,
        value="alpha",
        provenance=prov_alpha,
    )

    fact_beta = NormalizedEvidenceFact(
        fact_id=compute_fact_id(
            doc_id, "--mode", SemanticPredicate.ENUMERATES.value,
            "beta", prov_beta.model_dump(),
        ),
        document_id=doc_id,
        subject="--mode",
        predicate=SemanticPredicate.ENUMERATES,
        value="beta",
        provenance=prov_beta,
    )

    document = _document(
        source_id=source_id,
        source_sha256=source_sha256,
        facts=[fact_alpha, fact_beta],
    )

    constraints = extract_constraints(document)
    mode_constraints = [
        constraint for constraint in constraints
        if constraint.target_entity == "--mode"
    ]

    assert len(mode_constraints) == 1

    constraint = mode_constraints[0]
    assert isinstance(constraint, EnumConstraint)
    assert constraint.target_entity == "--mode"
    assert sorted(constraint.allowed_values) == ["alpha", "beta"]
    assert sorted(constraint.source_fact_ids) == sorted(
        [fact_alpha.fact_id, fact_beta.fact_id]
    )

    fact_index = {fact.fact_id: fact for fact in document.facts}
    for fact_id in constraint.source_fact_ids:
        fact = fact_index[fact_id]
        assert fact.provenance.line_start in {42, 43}
        assert fact.provenance.section == "Options"


def test_unenumerated_string_compiles_to_type_constraint():
    source_id = "handbrake_cli_help"
    source_sha256 = "0" * 64
    doc_id = compute_document_id(source_id, source_sha256)
    provenance = _make_provenance(10, "--preset <string>")

    fact = NormalizedEvidenceFact(
        fact_id=compute_fact_id(
            doc_id,
            "--preset",
            SemanticPredicate.ACCEPTS_TYPE.value,
            "string",
            provenance.model_dump(),
        ),
        document_id=doc_id,
        subject="--preset",
        predicate=SemanticPredicate.ACCEPTS_TYPE,
        value="string",
        provenance=provenance,
    )

    document = _document(
        source_id=source_id,
        source_sha256=source_sha256,
        facts=[fact],
    )

    constraints = extract_constraints(document)

    assert len(constraints) == 1
    constraint = constraints[0]
    assert isinstance(constraint, TypeConstraint)
    assert constraint.target_entity == "--preset"
    assert constraint.expected_type == "string"
    assert constraint.source_fact_ids == [fact.fact_id]
    assert not any(isinstance(c, EnumConstraint) for c in constraints)
