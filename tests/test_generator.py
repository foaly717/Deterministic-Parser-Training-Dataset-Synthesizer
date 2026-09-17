import json
from pathlib import Path

from dataset_tools.generator.prompt import (
    build_candidate_prompt,
    format_evidence_context,
)
from dataset_tools.generator.runner import (
    save_candidates,
    validate_candidate_structure,
)
from dataset_tools.parsers.cli_help import parse_cli_help


HELP_PATH = Path("data/evidence/handbrakecli-help.txt")


def test_prompt_formatting():
    facts = parse_cli_help(HELP_PATH)
    context = format_evidence_context(facts[:5])
    assert "--preset" in context
    assert "Select preset by name" in context
    assert "source lines:" in context
    assert "argument: <string>" in context
    prompt = build_candidate_prompt(facts[:5])
    assert "Target CLI evidence:" in prompt
    assert "Generate exactly ONE high-quality" in prompt


def test_prompt_rejects_empty_evidence():
    try:
        build_candidate_prompt([])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_candidate_structure_accepts_valid_record():
    item = {
        "instruction": "Encode using the documented preset example.",
        "context": None,
        "response": "HandBrakeCLI -i input.mkv -o output.mp4 --preset 'Preset Name'",
    }
    assert validate_candidate_structure(item)


def test_candidate_structure_rejects_missing_fields():
    item = {
        "instruction": "Encode a video.",
        "response": "HandBrakeCLI -i input.mkv -o output.mp4",
    }
    assert not validate_candidate_structure(item)


def test_candidate_structure_rejects_empty_fields():
    item = {
        "instruction": "",
        "context": None,
        "response": "HandBrakeCLI -i input.mkv -o output.mp4",
    }
    assert not validate_candidate_structure(item)


def test_candidate_structure_rejects_invalid_context():
    item = {
        "instruction": "Encode a video.",
        "context": 123,
        "response": "HandBrakeCLI -i input.mkv -o output.mp4",
    }
    assert not validate_candidate_structure(item)


def test_candidate_saving(tmp_path):
    test_out = tmp_path / "candidates.jsonl"
    dummy_responses = [
        {
            "instruction": "Encode using the documented preset example.",
            "context": None,
            "response": "HandBrakeCLI -i input.mkv -o output.mp4 --preset 'Preset Name'",
        },
        {
            "instruction": "",
            "context": None,
            "response": "invalid",
        },
    ]
    saved = save_candidates(
        raw_responses=dummy_responses,
        source_sha256="dummy_hash",
        generator_model="test_model",
        output_path=test_out,
    )
    assert saved == 1
    lines = test_out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["generator_model"] == "test_model"
    assert data["status"] == "candidate"
    assert data["source_sha256"] == "dummy_hash"
    assert data["instruction"]
    assert data["response"]
