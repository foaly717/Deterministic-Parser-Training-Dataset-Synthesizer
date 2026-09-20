from dataclasses import dataclass

from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.schema import (
    DerivedConstraint,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    SemanticPredicate,
)


@dataclass(frozen=True)
class PreparedEvidence:
    document: NormalizedEvidenceDocument
    constraints: tuple[DerivedConstraint, ...]
    cli_option_facts: tuple[NormalizedEvidenceFact, ...]
    valid_options: frozenset[str]
    expected_tool: str


def prepare_evidence(
    document: NormalizedEvidenceDocument,
) -> PreparedEvidence:
    cli_option_facts = tuple(
        fact
        for fact in document.facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    )

    if not cli_option_facts:
        raise ValueError(
            "Evidence document contains no supported CLI options."
        )

    if document.metadata.tool is None:
        raise ValueError(
            "Evidence document must identify exactly one CLI tool."
        )

    return PreparedEvidence(
        document=document,
        constraints=tuple(extract_constraints(document)),
        cli_option_facts=cli_option_facts,
        valid_options=frozenset(
            str(fact.value)
            for fact in cli_option_facts
        ),
        expected_tool=document.metadata.tool.name,
    )
