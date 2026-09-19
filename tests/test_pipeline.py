from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.evidence.schema import (
    EnumConstraint,
    FactCategory,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)
from dataset_tools.validators.pipeline import validate_candidate


PROVENANCE = Provenance(
    source_id="pipeline-test",
    source_sha256="abc123",
)


def _document(
    *,
    options: set[str],
    enum_values: dict[str, set[str]] | None = None,
) -> NormalizedEvidenceDocument:
    facts = [
        NormalizedEvidenceFact(
            fact_id=f"option-{option}",
            document_id="pipeline-doc",
            category=FactCategory.CLI_OPTION,
            subject="HandBrakeCLI",
            predicate="supports",
            value=option,
            provenance=PROVENANCE,
        )
        for option in sorted(options)
    ]

    for option, values in (enum_values or {}).items():
        for value in sorted(values):
            facts.append(
                NormalizedEvidenceFact(
                    fact_id=f"{option}-{value}",
                    document_id="pipeline-doc",
                    category=FactCategory.ENUM_VALUE,
                    subject=option,
                    predicate="enumerates",
                    value=value,
                    provenance=PROVENANCE,
                )
            )

    return NormalizedEvidenceDocument(
        document_id="pipeline-doc",
        source_id="pipeline-test",
        source_type="test",
        source_sha256="abc123",
        facts=facts,
    )


def _prepared(
    *,
    options: set[str],
    enum_values: dict[str, set[str]] | None = None,
):
    return prepare_evidence(
        _document(
            options=options,
            enum_values=enum_values,
        )
    )


def candidate(response: str) -> dict:
    return {
        "instruction": "Use the documented CLI option.",
        "context": None,
        "response": response,
    }


VALID_OPTIONS = {
    "--preset-export",
    "--preset-import-file",
}


def test_pipeline_accepts_valid_candidate():
    prepared = _prepared(options=VALID_OPTIONS)

    result = validate_candidate(
        candidate("HandBrakeCLI --preset-export MyPreset"),
        prepared,
    )

    assert result.status == "accepted"
    assert result.stage == "complete"
    assert result.validation_logs == [
        "Structural validation passed.",
        "All detected options are supported by supplied evidence.",
    ]


def test_pipeline_rejects_invalid_executable_before_options():
    prepared = _prepared(options=VALID_OPTIONS)

    result = validate_candidate(
        candidate("preset-tool --preset-export MyPreset"),
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "command"
    assert result.validation_logs == [
        "Structural validation passed.",
        "Unexpected executable detected: 'preset-tool'",
    ]


def test_pipeline_rejects_unsupported_option():
    prepared = _prepared(options=VALID_OPTIONS)

    result = validate_candidate(
        candidate("HandBrakeCLI --not-a-real-option value"),
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "options"
    assert result.validation_logs == [
        "Structural validation passed.",
        "Unsupported options detected: ['--not-a-real-option']",
    ]


def test_pipeline_rejects_structurally_invalid_candidate():
    prepared = _prepared(options=VALID_OPTIONS)

    result = validate_candidate(
        {
            "instruction": "",
            "context": None,
            "response": "HandBrakeCLI",
        },
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "structure"
    assert result.validation_logs == [
        "Structural validation failed."
    ]


def test_pipeline_rejects_unsupported_enum_value_with_reason_code():
    prepared = _prepared(
        options={"--preset"},
        enum_values={
            "--preset": {"Very Fast 1080p30"},
        },
    )

    result = validate_candidate(
        candidate('HandBrakeCLI --preset "Nonexistent Preset"'),
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "constraints"
    assert result.reason_code == "UNSUPPORTED_ENUM_VALUE"
    assert (
        "Unsupported value for --preset: Nonexistent Preset"
        in result.validation_logs[-1]
    )


def test_pipeline_rejects_unsupported_option_with_reason_code():
    prepared = _prepared(options={"--preset"})

    result = validate_candidate(
        candidate("HandBrakeCLI --not-a-real-option value"),
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "options"
    assert result.reason_code == "UNSUPPORTED_OPTION"


def test_pipeline_rejects_unexpected_executable_with_reason_code():
    prepared = _prepared(options={"--preset"})

    result = validate_candidate(
        candidate("preset-tool --preset value"),
        prepared,
    )

    assert result.status == "rejected"
    assert result.stage == "command"
    assert result.reason_code == "UNEXPECTED_EXECUTABLE"
