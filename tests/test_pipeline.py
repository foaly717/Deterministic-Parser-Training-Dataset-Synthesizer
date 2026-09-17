from dataset_tools.validators.pipeline import validate_candidate


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
        VALID_OPTIONS,
    )

    assert result.status == "accepted"
    assert result.stage == "complete"
    assert len(result.validation_logs) == 3


def test_pipeline_rejects_invalid_executable_before_options():
    result = validate_candidate(
        candidate("preset-tool --preset-export MyPreset"),
        "HandBrakeCLI",
        VALID_OPTIONS,
    )

    assert result.status == "rejected"
    assert result.stage == "command"
    assert len(result.validation_logs) == 2
    assert "Unexpected executable" in result.validation_logs[-1]


def test_pipeline_rejects_unsupported_option():
    result = validate_candidate(
        candidate("HandBrakeCLI --not-a-real-option value"),
        "HandBrakeCLI",
        VALID_OPTIONS,
    )

    assert result.status == "rejected"
    assert result.stage == "options"
    assert len(result.validation_logs) == 3
    assert "Unsupported options" in result.validation_logs[-1]


def test_pipeline_rejects_structurally_invalid_candidate():
    result = validate_candidate(
        {"instruction": "", "context": None, "response": "HandBrakeCLI"},
        "HandBrakeCLI",
        VALID_OPTIONS,
    )

    assert result.status == "rejected"
    assert result.stage == "structure"
    assert result.validation_logs == ["Structural validation failed."]
