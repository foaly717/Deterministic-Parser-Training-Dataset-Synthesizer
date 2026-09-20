import pytest

from dataset_tools.evidence.ids import compute_document_id, compute_fact_id
from dataset_tools.evidence.schema import (
    NormalizedEvidenceFact,
    Provenance,
    SemanticPredicate,
)
from dataset_tools.generator.prompt import (
    build_single_fact_prompt,
    format_evidence_context,
)


@pytest.fixture
def sample_fact():
    source_id = "handbrake-help"
    source_sha256 = "0" * 64
    doc_id = compute_document_id(source_id, source_sha256)

    provenance = Provenance(
        line_start=10,
        line_end=12,
        section="Options",
        raw_snippet="--preset <string>",
    )

    return NormalizedEvidenceFact(
        fact_id=compute_fact_id(
            doc_id,
            "HandBrakeCLI",
            SemanticPredicate.SUPPORTS.value,
            "--preset",
            provenance.model_dump(),
        ),
        document_id=doc_id,
        subject="HandBrakeCLI",
        predicate=SemanticPredicate.SUPPORTS,
        value="--preset",
        provenance=provenance,
    )


def test_format_evidence_context(sample_fact):
    context = format_evidence_context([sample_fact])

    assert "subject: HandBrakeCLI" in context
    assert "predicate: supports" in context
    assert "value: --preset" in context
    assert "source lines: 10-12" in context
    assert "section: Options" in context
    assert "source text: --preset <string>" in context
    assert "aliases:" not in context
    assert "argument:" not in context
    assert "description:" not in context


def test_build_single_fact_prompt(sample_fact):
    prompt = build_single_fact_prompt(sample_fact)
    assert "demonstrating this documented capability" in prompt
