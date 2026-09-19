from pathlib import Path

import pytest

from dataset_tools.candidates.parser import (
    CandidateParseError,
    parse_candidate,
)
from dataset_tools.evidence.loaders.handbrakecli import HandBrakeCliLoader
from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.generator import GenerationRequest, Generator
from dataset_tools.llm.mock import MockLLMClient


@pytest.fixture
def prepared_evidence():
    document = HandBrakeCliLoader().load(
        Path("data/evidence/handbrakecli-help.txt")
    )
    return prepare_evidence(document)


def test_parse_candidate_accepts_one_json_object():
    candidate = parse_candidate(
        '{"instruction":"Do something",'
        '"context":null,'
        '"response":"HandBrakeCLI --preset Test"}'
    )

    assert candidate["instruction"] == "Do something"
    assert candidate["context"] is None
    assert candidate["response"] == "HandBrakeCLI --preset Test"


def test_parse_candidate_rejects_invalid_json():
    with pytest.raises(CandidateParseError):
        parse_candidate("not json")


def test_parse_candidate_rejects_json_array():
    with pytest.raises(CandidateParseError):
        parse_candidate(
            '[{"instruction":"Do something",'
            '"context":null,'
            '"response":"HandBrakeCLI --preset Test"}]'
        )


def test_parse_candidate_preserves_schema_validation_boundary():
    raw_output = (
        '{"instruction":123,'
        '"context":{"unexpected":"type"},'
        '"extra":"allowed at parser boundary"}'
    )

    candidate = parse_candidate(raw_output)

    assert candidate == {
        "instruction": 123,
        "context": {"unexpected": "type"},
        "extra": "allowed at parser boundary",
    }

    from dataset_tools.validators.structure import (
        validate_candidate_structure,
    )

    assert validate_candidate_structure(candidate) is False


def test_generator_uses_prepared_evidence_and_parses_model_output(
    prepared_evidence,
):
    llm = MockLLMClient()
    generator = Generator(llm)

    result = generator.generate(
        prepared_evidence,
        GenerationRequest(
            fact_id=prepared_evidence.cli_option_facts[0].fact_id,
            max_tokens=321,
        ),
    )

    assert result.candidate["instruction"]
    assert result.candidate["response"]
    assert result.raw_output == llm.response
    assert result.prompt.startswith(
        "You are an automated training data generation engine."
    )

    assert len(llm.calls) == 1
    prompt, max_tokens = llm.calls[0]

    assert prompt == result.prompt
    assert max_tokens == 321


def test_generator_selection_is_deterministic(prepared_evidence):
    llm = MockLLMClient()
    generator = Generator(llm)

    selected_fact = prepared_evidence.cli_option_facts[3]

    result = generator.generate(
        prepared_evidence,
        GenerationRequest(
            fact_id=selected_fact.fact_id,
        ),
    )

    assert f"name: {selected_fact.value}" in result.prompt


def test_generator_rejects_unknown_fact_id(prepared_evidence):
    generator = Generator(MockLLMClient())

    with pytest.raises(KeyError, match="Requested fact_id"):
        generator.generate(
            prepared_evidence,
            GenerationRequest(
                fact_id="missing-fact-id",
            ),
        )


def test_generator_rejects_invalid_max_tokens(prepared_evidence):
    generator = Generator(MockLLMClient())

    with pytest.raises(ValueError, match="max_tokens must be >= 1"):
        generator.generate(
            prepared_evidence,
            GenerationRequest(
                fact_id=prepared_evidence.cli_option_facts[0].fact_id,
                max_tokens=0,
            ),
        )
