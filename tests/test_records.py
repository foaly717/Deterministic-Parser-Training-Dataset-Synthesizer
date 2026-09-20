"""Tests for the canonical RunRecord and identity contract."""

import hashlib
import io
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from dataset_tools.evidence.preparation import PreparedEvidence
from dataset_tools.evidence.schema import NormalizedEvidenceDocument
from dataset_tools.records.builder import (
    build_run_record,
    compute_prompt_sha256,
)
from dataset_tools.records.model import (
    CandidateModel,
    RunRecord,
    ValidationBlock,
    ValidationStage,
    example_id,
    normalize_text,
)
from dataset_tools.records.serialization import (
    serialize_run_record,
    write_run_record,
)
from dataset_tools.validators.reason_codes import ValidationReasonCode


SOURCE_SHA256 = "a" * 64
FACT_ID = "fact-test-001"
PROMPT = "Generate exactly one candidate for fact-test-001."
PROVIDER = "test-provider"
MODEL = "test-model"
MAX_TOKENS = 128


def make_prepared() -> PreparedEvidence:
    document = NormalizedEvidenceDocument(
        document_id="document-test-001",
        source_id="source-test",
        source_type="text",
        source_sha256=SOURCE_SHA256,
        facts=[],
        metadata={},
    )

    return PreparedEvidence(
        document=document,
        constraints=(),
        cli_option_facts=(),
        valid_options=frozenset({"--preset-export"}),
        expected_tool="HandBrakeCLI",
    )


def test_normalize_text_contract():
    assert normalize_text(None) is None
    assert normalize_text("") == ""
    assert normalize_text("  hello  ") == "hello"
    assert normalize_text("\t hello \t") == "hello"
    assert normalize_text("a\r\nb") == "a\nb"
    assert normalize_text("a\rb") == "a\rb"
    assert normalize_text("  a  b  ") == "a  b"


def test_example_id_is_deterministic():
    first = example_id(
        "  instruction  ",
        " context ",
        " response\r\n",
    )
    second = example_id(
        "instruction",
        "context",
        "response\n",
    )

    assert first == second
    assert len(first) == 64
    assert all(character in "0123456789abcdef" for character in first)


def test_example_id_preserves_none_vs_empty_context():
    none_context = example_id("instruction", None, "response")
    empty_context = example_id("instruction", "", "response")

    assert none_context != empty_context


def test_candidate_model_forbids_extra_fields():
    with pytest.raises(ValidationError):
        CandidateModel(
            instruction="instruction",
            context=None,
            response="response",
            unexpected="value",
        )


def test_validation_block_uses_canonical_reason_codes():
    block = ValidationBlock(
        status="rejected",
        stage=ValidationStage.PARSE,
        reason_code=ValidationReasonCode.INVALID_JSON,
        validation_logs=["bad json"],
    )

    assert block.reason_code is ValidationReasonCode.INVALID_JSON


def test_run_record_requires_candidate_and_example_id_together():
    with pytest.raises(ValidationError, match="candidate and example_id"):
        RunRecord(
            fact_id=FACT_ID,
            source_sha256=SOURCE_SHA256,
            generator_provider=PROVIDER,
            generator_model=MODEL,
            max_tokens=MAX_TOKENS,
            prompt_sha256=compute_prompt_sha256(PROMPT),
            raw_response="{}",
            candidate=CandidateModel(
                instruction="instruction",
                context=None,
                response="response",
            ),
            example_id=None,
            validation=ValidationBlock(
                status="accepted",
                stage=ValidationStage.COMPLETE,
            ),
        )


def test_run_record_requires_normalized_candidate():
    candidate = CandidateModel(
        instruction=" instruction ",
        context=None,
        response="response",
    )

    with pytest.raises(ValidationError, match="instruction is not normalized"):
        RunRecord(
            fact_id=FACT_ID,
            source_sha256=SOURCE_SHA256,
            generator_provider=PROVIDER,
            generator_model=MODEL,
            max_tokens=MAX_TOKENS,
            prompt_sha256=compute_prompt_sha256(PROMPT),
            raw_response="{}",
            candidate=candidate,
            example_id=example_id(
                " instruction ",
                None,
                "response",
            ),
            validation=ValidationBlock(
                status="accepted",
                stage=ValidationStage.COMPLETE,
            ),
        )


def test_run_record_recomputes_example_identity():
    candidate = CandidateModel(
        instruction="instruction",
        context=None,
        response="response",
    )

    with pytest.raises(
        ValidationError,
        match="Stored example_id does not match",
    ):
        RunRecord(
            fact_id=FACT_ID,
            source_sha256=SOURCE_SHA256,
            generator_provider=PROVIDER,
            generator_model=MODEL,
            max_tokens=MAX_TOKENS,
            prompt_sha256=compute_prompt_sha256(PROMPT),
            raw_response="{}",
            candidate=candidate,
            example_id="0" * 64,
            validation=ValidationBlock(
                status="accepted",
                stage=ValidationStage.COMPLETE,
            ),
        )


def test_run_record_accepts_canonical_candidate():
    candidate = CandidateModel(
        instruction="instruction",
        context=None,
        response="response",
    )
    identity = example_id(
        candidate.instruction,
        candidate.context,
        candidate.response,
    )

    record = RunRecord(
        fact_id=FACT_ID,
        source_sha256=SOURCE_SHA256,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
        prompt_sha256=compute_prompt_sha256(PROMPT),
        raw_response='{"instruction":"instruction"}',
        candidate=candidate,
        example_id=identity,
        validation=ValidationBlock(
            status="accepted",
            stage=ValidationStage.COMPLETE,
        ),
    )

    assert record.schema_version == 1
    assert record.candidate == candidate
    assert record.example_id == identity


def test_prompt_sha256_hashes_exact_utf8_prompt():
    prompt = "héllo\n"
    expected = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    assert compute_prompt_sha256(prompt) == expected


def test_parse_failure_produces_record_without_candidate():
    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response="not json",
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage is ValidationStage.PARSE
    assert record.validation.reason_code is ValidationReasonCode.INVALID_JSON
    assert record.candidate is None
    assert record.example_id is None
    assert record.raw_response == "not json"
    assert record.source_sha256 == SOURCE_SHA256


def test_json_shape_failure_produces_record_without_candidate():
    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response="[]",
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage is ValidationStage.PARSE
    assert (
        record.validation.reason_code
        is ValidationReasonCode.INVALID_JSON_SHAPE
    )
    assert record.candidate is None
    assert record.example_id is None


def test_structural_failure_produces_record_without_candidate():
    raw_response = json.dumps(
        {
            "instruction": "",
            "context": None,
            "response": "HandBrakeCLI",
        }
    )

    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response=raw_response,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage is ValidationStage.STRUCTURE
    assert (
        record.validation.reason_code
        is ValidationReasonCode.INVALID_STRUCTURE
    )
    assert record.validation.validation_logs == [
        "Structural validation failed."
    ]
    assert record.candidate is None
    assert record.example_id is None


def test_successful_structural_candidate_is_normalized_before_persistence():
    raw_response = json.dumps(
        {
            "instruction": "  instruction  ",
            "context": " context ",
            "response": " HandBrakeCLI ",
        }
    )

    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response=raw_response,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.candidate is not None
    assert record.candidate.instruction == "instruction"
    assert record.candidate.context == "context"
    assert record.candidate.response == "HandBrakeCLI"
    assert record.example_id == example_id(
        "instruction",
        "context",
        "HandBrakeCLI",
    )


def test_domain_rejection_retains_candidate_and_identity():
    raw_response = json.dumps(
        {
            "instruction": "instruction",
            "context": None,
            "response": "ffmpeg -i input.mp4",
        }
    )

    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response=raw_response,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage is ValidationStage.COMMAND
    assert (
        record.validation.reason_code
        is ValidationReasonCode.UNEXPECTED_EXECUTABLE
    )
    assert record.candidate is not None
    assert record.example_id == example_id(
        record.candidate.instruction,
        record.candidate.context,
        record.candidate.response,
    )


def test_empty_successful_response_is_parse_failure():
    record = build_run_record(
        prepared=make_prepared(),
        fact_id=FACT_ID,
        prompt=PROMPT,
        raw_response="",
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
    )

    assert record.validation.status == "rejected"
    assert record.validation.stage is ValidationStage.PARSE
    assert record.validation.reason_code is ValidationReasonCode.INVALID_JSON
    assert record.raw_response == ""


def test_serialization_is_deterministic():
    candidate = CandidateModel(
        instruction="instruction",
        context=None,
        response="response",
    )
    identity = example_id(
        candidate.instruction,
        candidate.context,
        candidate.response,
    )

    record = RunRecord(
        fact_id=FACT_ID,
        source_sha256=SOURCE_SHA256,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
        prompt_sha256=compute_prompt_sha256(PROMPT),
        raw_response="raw",
        candidate=candidate,
        example_id=identity,
        validation=ValidationBlock(
            status="accepted",
            stage=ValidationStage.COMPLETE,
            validation_logs=["ok"],
        ),
    )

    first = serialize_run_record(record)
    second = serialize_run_record(record)

    assert first == second
    assert "\n" not in first
    assert "\r" not in first


def test_writer_emits_exactly_one_newline():
    candidate = CandidateModel(
        instruction="instruction",
        context=None,
        response="response",
    )
    identity = example_id(
        candidate.instruction,
        candidate.context,
        candidate.response,
    )

    record = RunRecord(
        fact_id=FACT_ID,
        source_sha256=SOURCE_SHA256,
        generator_provider=PROVIDER,
        generator_model=MODEL,
        max_tokens=MAX_TOKENS,
        prompt_sha256=compute_prompt_sha256(PROMPT),
        raw_response="raw",
        candidate=candidate,
        example_id=identity,
        validation=ValidationBlock(
            status="accepted",
            stage=ValidationStage.COMPLETE,
        ),
    )

    stream = io.StringIO()
    write_run_record(record, stream)

    output = stream.getvalue()

    assert output.endswith("\n")
    assert not output.endswith("\n\n")
    assert output.count("\n") == 1
    assert json.loads(output)["schema_version"] == 1


# ---------------------------------------------------------------------------
# Golden fixture contract
# ---------------------------------------------------------------------------




def test_golden_fixture_has_expected_four_record_shapes():
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "run_records.golden.jsonl"
    )

    lines = fixture.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 4

    records = [json.loads(line) for line in lines]

    assert [
        (
            record["validation"]["status"],
            record["validation"]["stage"],
            record["validation"]["reason_code"],
        )
        for record in records
    ] == [
        ("accepted", "complete", None),
        ("rejected", "command", "UNEXPECTED_EXECUTABLE"),
        ("rejected", "parse", "INVALID_JSON"),
        ("rejected", "structure", "INVALID_STRUCTURE"),
    ]

    assert records[0]["candidate"] is not None
    assert records[0]["example_id"] is not None

    assert records[1]["candidate"] is not None
    assert records[1]["example_id"] is not None

    assert records[2]["candidate"] is None
    assert records[2]["example_id"] is None

    assert records[3]["candidate"] is None
    assert records[3]["example_id"] is None


def test_golden_fixture_example_ids_are_independent_constants():
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "run_records.golden.jsonl"
    )

    records = [
        json.loads(line)
        for line in fixture.read_text(encoding="utf-8").splitlines()
    ]

    assert records[0]["example_id"] == (
        "d987045fc79e4ecae57320d6a98dd0d8afb78d27a75203940a481efdf0805e69"
    )
    assert records[1]["example_id"] == (
        "9521d6258b21379cb47d81d8c409cf483f36574653ad2db679d27940f5e69ea8"
    )


def test_golden_fixture_prompt_hashes_are_independent_constants():
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "run_records.golden.jsonl"
    )

    records = [
        json.loads(line)
        for line in fixture.read_text(encoding="utf-8").splitlines()
    ]

    assert records[0]["prompt_sha256"] == (
        "31f4bae2bffe80e7a7e9eb5ca0dd5a6cd95fb4a787b70e4e5c77cddc29324582"
    )
    assert records[1]["prompt_sha256"] == (
        "d440a78d3655edade5c33346a3dab7129a2c8bd664c9363026558c4a2bf54713"
    )
    assert records[2]["prompt_sha256"] == (
        "64a9ae667656427dd5f7e624c1017e30f4bff11baabf82d2871b349ddd4131e8"
    )
    assert records[3]["prompt_sha256"] == (
        "bcddb9cf5b191e685433c621a517a18d4aae3a75fe04d491f5d8ef841e8294fd"
    )


def test_golden_fixture_has_expected_sha256():
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "run_records.golden.jsonl"
    )

    digest = hashlib.sha256(
        fixture.read_bytes()
    ).hexdigest()

    assert digest == "f1ad3411b73e50d1d95b83055f22f8f556d7d183cd162f5496be381aa25ab830"
