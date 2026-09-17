import pytest
from dataset_tools.evidence.schema import NormalizedEvidenceFact
from dataset_tools.generator.prompt import format_evidence_context, build_candidate_prompt, build_single_fact_prompt


@pytest.fixture
def sample_fact():
    return NormalizedEvidenceFact(
        subject="HandBrakeCLI",
        category="cli_option",
        predicate="supports",
        value="--preset",
        metadata={
            "aliases": ["-Z"],
            "argument": "<string>",
            "description": "Select preset",
            "source_line_start": 10,
            "source_line_end": 12,
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
