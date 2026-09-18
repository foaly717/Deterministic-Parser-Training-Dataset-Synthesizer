from dataclasses import dataclass, field

from dataset_tools.evidence.schema import (
    DerivedConstraint,
    NormalizedEvidenceDocument,
)


@dataclass
class EvidenceIndex:
    valid_options: set[str] = field(default_factory=set)
    constraints: dict[str, set[str]] = field(default_factory=dict)


def build_evidence_index(
    document: NormalizedEvidenceDocument,
    constraints: list[DerivedConstraint] | None = None,
) -> EvidenceIndex:
    valid_options: set[str] = set()
    constraint_values: dict[str, set[str]] = {}

    for fact in document.facts:
        if fact.category == "cli_option" and fact.predicate == "supports":
            valid_options.add(str(fact.value))

    for constraint in constraints or []:
        if hasattr(constraint, "allowed_values"):
            allowed_values = getattr(constraint, "allowed_values")
            if allowed_values:
                constraint_values.setdefault(
                    constraint.target_entity,
                    set(),
                ).update(allowed_values)

    return EvidenceIndex(
        valid_options=valid_options,
        constraints=constraint_values,
    )
