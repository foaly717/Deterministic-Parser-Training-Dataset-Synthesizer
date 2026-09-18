from types import SimpleNamespace

from dataset_tools.evidence.index import build_evidence_index
from dataset_tools.evidence.schema import (
    EnumConstraint,
    FactCategory,
    NormalizedEvidenceFact,
    Provenance,
)


def test_evidence_index_collects_options_and_constraints():
    provenance = Provenance(
        source_id="example-help",
        source_sha256="abc",
    )

    facts = [
        NormalizedEvidenceFact(
            fact_id="fact-option",
            document_id="doc",
            category=FactCategory.CLI_OPTION,
            subject="ExampleCLI",
            predicate="supports",
            value="--mode",
            provenance=provenance,
        ),
    ]

    constraint = EnumConstraint(
        constraint_id="constraint-mode",
        target_entity="--mode",
        source_fact_ids=["fact-alpha"],
        allowed_values=[
            "alpha",
            "beta",
        ],
    )

    document = SimpleNamespace(
        facts=facts,
    )

    index = build_evidence_index(
        document,
        constraints=[constraint],
    )

    assert "--mode" in index.valid_options
    assert "--mode" in index.constraints
    assert "alpha" in index.constraints["--mode"]
