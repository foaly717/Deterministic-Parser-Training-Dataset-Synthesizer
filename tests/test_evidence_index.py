import pytest
from types import SimpleNamespace
from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.evidence.schema import NormalizedEvidenceFact


def test_evidence_index_collects_options_and_constraints():
    facts = [
        NormalizedEvidenceFact(
            subject="HandBrakeCLI",
            category="cli_option",
            predicate="supports",
            value="--preset",
            metadata={},
        ),
        NormalizedEvidenceFact(
            subject="--preset",
            category="cli_constraint",
            predicate="allows",
            value="Very Fast 1080p30",
            extraction_type="enum",
            metadata={"allowed_values": {"Very Fast 1080p30", "HQ 1080p30 Surround"}},
        ),
    ]
    document = SimpleNamespace(facts=facts)
    
    index = build_evidence_index(document)
    
    assert "--preset" in index.valid_options
    assert "--preset" in index.constraints
    assert "Very Fast 1080p30" in index.constraints["--preset"]
