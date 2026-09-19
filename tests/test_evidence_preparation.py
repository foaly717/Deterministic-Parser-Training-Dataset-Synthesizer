from pathlib import Path

from dataset_tools.evidence.preparation import prepare_evidence
from dataset_tools.evidence.registry import load_evidence
from dataset_tools.evidence.schema import EnumConstraint


def test_prepare_evidence_builds_authoritative_operational_view():
    document = load_evidence(
        Path("data/evidence/handbrakecli-help.txt")
    )

    prepared = prepare_evidence(document)

    assert prepared.document is document
    assert prepared.expected_tool == "HandBrakeCLI"
    assert "--format" in prepared.valid_options
    assert "--encoder" in prepared.valid_options
    assert prepared.cli_option_facts

    format_constraint = next(
        constraint
        for constraint in prepared.constraints
        if (
            isinstance(constraint, EnumConstraint)
            and constraint.target_entity == "--format"
        )
    )

    assert set(format_constraint.allowed_values) == {
        "av_mkv",
        "av_mp4",
        "av_webm",
    }


def test_prepare_evidence_derives_constraints_once():
    document = load_evidence(
        Path("data/evidence/handbrakecli-help.txt")
    )

    prepared = prepare_evidence(document)

    assert prepared.constraints
    assert all(
        constraint.source_fact_ids
        for constraint in prepared.constraints
    )


def test_prepare_evidence_rejects_document_without_cli_options():
    document = load_evidence(
        Path("data/evidence/sample-man-page.txt")
    )

    try:
        prepare_evidence(document)
    except ValueError as exc:
        assert str(exc) == (
            "Evidence document contains no supported CLI options."
        )
    else:
        raise AssertionError(
            "prepare_evidence() should reject evidence without CLI options"
        )
