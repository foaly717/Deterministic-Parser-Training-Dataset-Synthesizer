from pathlib import Path

from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
    SemanticPredicate,
    ToolIdentity,
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
        line_start=1,
        line_end=1,
        section="enum-integration",
    )

    document = NormalizedEvidenceDocument(
        document_id="enum-doc",
        artifact=ArtifactIdentity(
            source_id="enum-integration",
            source_sha256="abc123",
        ),
        metadata=DocumentMetadata(
            format=DocumentFormat.CLI_HELP,
            tool=ToolIdentity(name="ExampleCLI"),
        ),
        facts=[
            NormalizedEvidenceFact(
                fact_id="fact-mode",
                document_id="enum-doc",
                subject="ExampleCLI",
                predicate=SemanticPredicate.SUPPORTS,
                value="--mode",
                provenance=provenance,
            ),
            NormalizedEvidenceFact(
                fact_id="fact-alpha",
                document_id="enum-doc",
                subject="--mode",
                predicate=SemanticPredicate.ENUMERATES,
                value="alpha",
                provenance=provenance,
            ),
            NormalizedEvidenceFact(
                fact_id="fact-beta",
                document_id="enum-doc",
                subject="--mode",
                predicate=SemanticPredicate.ENUMERATES,
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
