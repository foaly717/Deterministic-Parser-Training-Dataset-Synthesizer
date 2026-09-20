import json
from pathlib import Path

from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.generator.orchestrator import GenerationRequest, Generator
from dataset_tools.llm.mock import MockLLMClient

from dataset_tools.records.builder import build_run_record, compute_prompt_sha256
from dataset_tools.records.model import example_id
from dataset_tools.validators.reason_codes import ValidationReasonCode


EVIDENCE_PATH = Path("data/evidence/handbrakecli-help.txt")


def _prepared_evidence():
    document = load_evidence(EVIDENCE_PATH)
    return prepare_evidence(document)


def _format_fact(prepared):
    return next(
        fact
        for fact in prepared.cli_option_facts
        if fact.value == "--format"
    )


def _generation_result(prepared, response):
    fact = _format_fact(prepared)
    request = GenerationRequest(
        fact_id=fact.fact_id,
        max_tokens=128,
    )
    client = MockLLMClient(response=response)
    generator = Generator(client)

    result = generator.generate(prepared, request)

    assert len(client.calls) == 1
    assert client.calls[0][1] == request.max_tokens

    return request, result


def _build_record(prepared, request, result):
    return build_run_record(
        prepared=prepared,
        fact_id=request.fact_id,
        prompt=result.prompt,
        raw_response=result.raw_output,
        generator_provider="test-provider",
        generator_model="test-model",
        max_tokens=request.max_tokens,
    )


def test_documented_enum_value_completes_generation_to_run_record():
    prepared = _prepared_evidence()

    raw_response = json.dumps(
        {
            "instruction": "Select the documented container format.",
            "context": None,
            "response": "HandBrakeCLI --format av_mp4",
        }
    )

    request, result = _generation_result(prepared, raw_response)
    record = _build_record(prepared, request, result)

    assert record.fact_id == request.fact_id
    assert record.source_sha256 == prepared.document.artifact.source_sha256
    assert record.raw_response == result.raw_output
    assert record.prompt_sha256 == compute_prompt_sha256(result.prompt)

    assert record.candidate is not None
    assert record.candidate.response == "HandBrakeCLI --format av_mp4"

    assert record.validation.status == "accepted"
    assert record.validation.stage == "complete"
    assert record.validation.reason_code is None

    assert record.example_id is not None
    assert record.example_id == example_id(record.candidate.instruction, record.candidate.context, record.candidate.response)


def test_fabricated_enum_value_is_rejected_by_constraints():
    prepared = _prepared_evidence()

    raw_response = json.dumps(
        {
            "instruction": "Select a container format.",
            "context": None,
            "response": "HandBrakeCLI --format fabricated_value",
        }
    )

    request, result = _generation_result(prepared, raw_response)
    record = _build_record(prepared, request, result)

    assert record.fact_id == request.fact_id
    assert record.source_sha256 == prepared.document.artifact.source_sha256
    assert record.raw_response == result.raw_output
    assert record.prompt_sha256 == compute_prompt_sha256(result.prompt)

    assert record.candidate is not None
    assert record.candidate.response == (
        "HandBrakeCLI --format fabricated_value"
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage == "constraints"
    assert (
        record.validation.reason_code
        == ValidationReasonCode.UNSUPPORTED_ENUM_VALUE
    )

    assert record.example_id is not None
    assert record.example_id == example_id(record.candidate.instruction, record.candidate.context, record.candidate.response)
