from pathlib import Path

from dataset_tools.evidence.registry import load_evidence


def test_handbrake_evidence_fixture_loads():
    source = Path("data/evidence/handbrakecli-help.txt")

    document = load_evidence(source)

    assert document.source.source_id == "handbrakecli-help"
    assert document.source.source_type == "text"
    assert document.source.sha256
    assert len(document.facts) > 0
    assert document.facts[0].category == "text"
