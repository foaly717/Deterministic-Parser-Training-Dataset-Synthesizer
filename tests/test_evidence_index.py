from types import SimpleNamespace

from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.evidence.schema import NormalizedEvidenceFact


def test_evidence_index_collects_options_and_constraints():
    facts = [
        NormalizedEvidenceFact(
            subject="ExampleCLI",
            category="cli_option",
            predicate="supports",
            value="--mode",
            metadata={},
        ),
        NormalizedEvidenceFact(
            subject="--mode",
            category="cli_constraint",
            predicate="allows",
            value="alpha",
            extraction_type="enum",
            metadata={"allowed_values": {"alpha", "beta"}},
        ),
    ]
    document = SimpleNamespace(facts=facts)

    index = build_evidence_index(document)

    assert "--mode" in index.valid_options
    assert "--mode" in index.constraints
    assert "alpha" in index.constraints["--mode"]
