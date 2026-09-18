import pytest

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    FactCategory,
    NormalizedEvidenceFact,
    Provenance,
)
from dataset_tools.generator.prompt import format_evidence_context, build_candidate_prompt, build_single_fact_prompt


@pytest.fixture
def sample_fact():
    source_id = "handbrake-help"
    source_sha256 = "0" * 64
    doc_id = document_id(source_id, source_sha256)

    provenance = Provenance(
        source_id=source_id,
        source_sha256=source_sha256,
        line_start=10,
        line_end=12,
        section="Options",
        raw_snippet="--preset <string>",
    )

    return NormalizedEvidenceFact(
        fact_id=fact_id(
            doc_id,
            "CLI_OPTION",
            "HandBrakeCLI",
            "supports",
            "--preset",
            provenance.model_dump(),
        ),
        document_id=doc_id,
        subject="HandBrakeCLI",
        category=FactCategory.CLI_OPTION,
        predicate="supports",
        value="--preset",
        provenance=provenance,
        metadata={
            "aliases": ["-Z"],
            "argument": "<string>",
            "description": "Select preset",
        },
    )


def test_format_evidence_context(sample_fact):
    context = format_evidence_context([sample_fact])
    assert "tool: HandBrakeCLI" in context
    assert "name: --preset" in context
    assert "aliases: -Z" in context


def test_build_candidate_prompt(sample_fact):
    prompt = build_candidate_prompt([sample_fact])
    assert "Target CLI evidence:" in prompt
    assert "HandBrakeCLI" in prompt


def test_build_single_fact_prompt(sample_fact):
    prompt = build_single_fact_prompt(sample_fact)
    assert "demonstrating this documented capability" in prompt
