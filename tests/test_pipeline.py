from dataset_tools.validators.pipeline import validate_candidate
from dataset_tools.evidence.index import EvidenceIndex


VALID_OPTIONS = {"--preset-export", "--preset-import-file"}


def candidate(response: str) -> dict:
    return {
        "instruction": "Use the documented CLI option.",
        "context": None,
        "response": response,
    }


def test_pipeline_accepts_valid_candidate():
    result = validate_candidate(
        candidate("HandBrakeCLI --preset-export MyPreset"),
        "HandBrakeCLI",
        EvidenceIndex(valid_options=VALID_OPTIONS),
    )

    assert result.status == "accepted"
    assert result.stage == "complete"
    assert result.validation_logs == [
        "Structural validation passed.",
        "Expected executable detected.",
        "All detected options are supported by supplied evidence.",
        "All detected constraints are satisfied.",
    ]


def test_pipeline_rejects_invalid_executable_before_options():
    result = validate_candidate(
        candidate("preset-tool --preset-export MyPreset"),
        "HandBrakeCLI",
        EvidenceIndex(valid_options=VALID_OPTIONS),
    )

    assert result.status == "rejected"
    assert result.stage == "command"
    assert result.validation_logs == [
        "Structural validation passed.",
        "Unexpected executable detected: 'preset-tool'",
    ]


def test_pipeline_rejects_unsupported_option():
    result = validate_candidate(
        candidate("HandBrakeCLI --not-a-real-option value"),
        "HandBrakeCLI",
        EvidenceIndex(valid_options=VALID_OPTIONS),
    )

    assert result.status == "rejected"
    assert result.stage == "options"
    assert result.validation_logs == [
        "Structural validation passed.",
        "Expected executable detected.",
        "Unsupported options detected: ['--not-a-real-option']",
    ]


def test_pipeline_rejects_structurally_invalid_candidate():
    result = validate_candidate(
        {"instruction": "", "context": None, "response": "HandBrakeCLI"},
        "HandBrakeCLI",
        EvidenceIndex(valid_options=VALID_OPTIONS),
    )

    assert result.status == "rejected"
    assert result.stage == "structure"
    assert result.validation_logs == ["Structural validation failed."]
