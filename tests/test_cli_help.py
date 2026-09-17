from pathlib import Path
import hashlib

from dataset_tools.parsers.cli_help import parse_cli_help


HELP = Path("data/evidence/handbrakecli-help.txt")


def facts():
    return parse_cli_help(HELP)


def get(name):
    matches = [f for f in facts() if f.name == name]
    assert len(matches) == 1
    return matches[0]


def test_preset():
    f = get("--preset")
    assert f.aliases == ["-Z"]
    assert f.argument == "<string>"
    assert f.line_start == 10
    assert f.line_end == 12
    assert f.parent_command is None
    assert "Select preset by name" in f.description


def test_audio():
    f = get("--audio")
    assert f.aliases == ["-a"]
    assert f.argument == "<string>"
    assert f.line_start == 183
    assert f.line_end == 186
    assert "Multiple output tracks" in f.description


def test_independent_rate_options():
    for name in ("--vfr", "--cfr", "--pfr"):
        f = get(name)
        assert f.aliases == []
        assert f.argument is None
        assert f.parent_command is None
        assert "frame rate control" in f.description


def test_multiline_description():
    f = get("--disable-hw-decoding")
    assert f.description == (
        "Disable hardware decoding of the video track,\n"
        "forcing software decoding instead"
    )


def test_source_provenance():
    text = HELP.read_text(encoding="utf-8")
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert get("--preset").source_sha256 == expected


def test_fact_count():
    assert len(facts()) == 151
