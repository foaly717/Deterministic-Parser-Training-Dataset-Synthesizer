from pathlib import Path

from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import (
    EnumConstraint,
    FactCategory,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)
from dataset_tools.validators.pipeline import validate_candidate


def _load_ffmpeg_evidence():
    document = load_evidence(
        Path("data/evidence/ffmpeg-help.txt")
    )
    return prepare_evidence(document)


def test_ffmpeg_documented_option_is_accepted():
    prepared = _load_ffmpeg_evidence()

    candidate = {
        "instruction": "Show ffmpeg version information.",
        "context": None,
        "response": "ffmpeg -version",
    }

    result = validate_candidate(candidate, prepared)

    assert result.status == "accepted"
    assert result.stage == "complete"


def test_ffmpeg_fabricated_option_is_rejected():
    prepared = _load_ffmpeg_evidence()

    candidate = {
        "instruction": "Use an unsupported ffmpeg option.",
        "context": None,
        "response": "ffmpeg --does-not-exist",
    }

    result = validate_candidate(candidate, prepared)

    assert result.status == "rejected"
    assert result.stage == "options"
    assert result.reason_code == "UNSUPPORTED_OPTION"


def test_fabricated_enum_value_is_rejected():
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
            ),
            NormalizedEvidenceFact(
                fact_id="fact-alpha",
                document_id="enum-doc",
                category=FactCategory.ENUM_VALUE,
                subject="--mode",
                predicate="enumerates",
                value="alpha",
                provenance=provenance,
            ),
            NormalizedEvidenceFact(
                fact_id="fact-beta",
                document_id="enum-doc",
                category=FactCategory.ENUM_VALUE,
                subject="--mode",
                predicate="enumerates",
                value="beta",
                provenance=provenance,
            ),
        ],
    )

    prepared = prepare_evidence(document)

    candidate = {
        "instruction": "Use an unsupported mode.",
        "context": None,
        "response": 'ExampleCLI --mode "gamma"',
    }

    result = validate_candidate(candidate, prepared)

    assert result.status == "rejected"
    assert result.stage == "constraints"
    assert result.reason_code == "UNSUPPORTED_ENUM_VALUE"
