from pathlib import Path

from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.validators.pipeline import validate_candidate


def _load_ffmpeg_index():
    document = load_evidence(
        Path("data/evidence/ffmpeg-help.txt")
    )

    constraints = extract_constraints(document)

    return build_evidence_index(
        document,
        constraints,
    )


def test_ffmpeg_documented_option_is_accepted():
    evidence_index = _load_ffmpeg_index()

    candidate = {
        "instruction": "Show ffmpeg version information.",
        "context": None,
        "response": "ffmpeg -version",
    }

    result = validate_candidate(
        candidate,
        "ffmpeg",
        evidence_index,
    )

    assert result.status == "accepted"
    assert result.stage == "complete"


def test_ffmpeg_fabricated_option_is_rejected():
    evidence_index = _load_ffmpeg_index()

    candidate = {
        "instruction": "Use an unsupported ffmpeg option.",
        "context": None,
        "response": "ffmpeg --does-not-exist",
    }

    result = validate_candidate(
        candidate,
        "ffmpeg",
        evidence_index,
    )

    assert result.status == "rejected"
    assert result.stage == "options"
    assert result.reason_code == "UNSUPPORTED_OPTION"


def test_fabricated_enum_value_is_rejected():
    from dataset_tools.evidence.schema import (
        EnumConstraint,
        FactCategory,
        NormalizedEvidenceDocument,
        NormalizedEvidenceFact,
        Provenance,
    )

    provenance = Provenance(
        source_id="enum-integration",
        source_sha256="abc123",
    )

    document = NormalizedEvidenceDocument(
        document_id="enum-doc",
        source_id="enum-integration",
        source_type="test",
        source_sha256="abc123",
        facts=[
            NormalizedEvidenceFact(
                fact_id="fact-mode",
                document_id="enum-doc",
                category=FactCategory.CLI_OPTION,
                subject="ExampleCLI",
                predicate="supports",
                value="--mode",
                provenance=provenance,
            )
        ],
    )

    constraint = EnumConstraint(
        constraint_id="mode-values",
        target_entity="--mode",
        source_fact_ids=["fact-mode"],
        allowed_values=["alpha", "beta"],
    )

    evidence_index = build_evidence_index(
        document,
        [constraint],
    )

    candidate = {
        "instruction": "Use an unsupported mode.",
        "context": None,
        "response": 'ExampleCLI --mode "gamma"',
    }

    result = validate_candidate(
        candidate,
        "ExampleCLI",
        evidence_index,
    )

    assert result.status == "rejected"
    assert result.stage == "constraints"
    assert result.reason_code == "UNSUPPORTED_ENUM_VALUE"
