from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from dataset_tools.evidence.extract_constraints import extract_constraints
from dataset_tools.evidence.schema import (
    DerivedConstraint,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)


@dataclass(frozen=True)
class PreparedEvidence:
    """Immutable operational view of normalized evidence."""

    document: NormalizedEvidenceDocument
    constraints: tuple[DerivedConstraint, ...]
    cli_option_facts: tuple[NormalizedEvidenceFact, ...]
    valid_options: frozenset[str]
    constraint_values: Mapping[str, frozenset[str]]
    expected_tool: str


def prepare_evidence(
    document: NormalizedEvidenceDocument,
) -> PreparedEvidence:
    """Prepare normalized evidence for generation and validation."""

    cli_option_facts = tuple(
        fact
        for fact in document.facts
        if (
            fact.category == "cli_option"
            and fact.predicate == "supports"
        )
    )

    if not cli_option_facts:
        raise ValueError(
            "Evidence document contains no supported CLI options."
        )

    tools = {
        fact.subject
        for fact in cli_option_facts
        if fact.subject
    }

    if len(tools) != 1:
        raise ValueError(
            "Evidence document must identify exactly one CLI tool."
        )

    constraints = tuple(extract_constraints(document))

    constraint_values: dict[str, frozenset[str]] = {}

    for constraint in constraints:
        allowed_values = getattr(
            constraint,
            "allowed_values",
            None,
        )

        if allowed_values:
            constraint_values[constraint.target_entity] = (
                frozenset(allowed_values)
            )

    return PreparedEvidence(
        document=document,
        constraints=constraints,
        cli_option_facts=cli_option_facts,
        valid_options=frozenset(
            str(fact.value)
            for fact in cli_option_facts
        ),
        constraint_values=MappingProxyType(
            constraint_values
        ),
        expected_tool=next(iter(tools)),
    )
