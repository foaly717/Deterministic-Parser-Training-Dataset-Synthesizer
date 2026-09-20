from collections import defaultdict

from dataset_tools.evidence.ids import compute_constraint_id
from dataset_tools.evidence.schema import (
    DependencyConstraint,
    DerivedConstraint,
    EnumConstraint,
    MutualExclusionConstraint,
    NormalizedEvidenceDocument,
    RangeConstraint,
    SemanticPredicate,
    TypeConstraint,
)


def extract_constraints(
    document: NormalizedEvidenceDocument,
) -> list[DerivedConstraint]:
    constraints: list[DerivedConstraint] = []
    enum_facts_by_subject: dict[str, list] = defaultdict(list)
    range_facts_by_subject: dict[str, list] = defaultdict(list)

    for fact in document.facts:
        if fact.predicate == SemanticPredicate.ENUMERATES:
            if not isinstance(fact.value, str):
                raise TypeError(
                    f"Enum constraint for {fact.subject} requires a string value, "
                    f"got {type(fact.value).__name__}: {fact.value!r}"
                )
            enum_facts_by_subject[fact.subject].append(fact)

        elif fact.predicate == SemanticPredicate.ACCEPTS_TYPE:
            cid = compute_constraint_id(
                "type",
                fact.subject,
                [fact.fact_id],
            )
            constraints.append(
                TypeConstraint(
                    constraint_id=cid,
                    target_entity=fact.subject,
                    source_fact_ids=[fact.fact_id],
                    expected_type=str(fact.value),
                )
            )

        elif fact.predicate in (
            SemanticPredicate.HAS_MINIMUM,
            SemanticPredicate.HAS_MAXIMUM,
        ):
            range_facts_by_subject[fact.subject].append(fact)

        elif fact.predicate == SemanticPredicate.REQUIRES:
            cid = compute_constraint_id(
                "dependency",
                fact.subject,
                [fact.fact_id],
            )
            constraints.append(
                DependencyConstraint(
                    constraint_id=cid,
                    target_entity=fact.subject,
                    source_fact_ids=[fact.fact_id],
                    requires=str(fact.value),
                )
            )

        elif fact.predicate == SemanticPredicate.CONFLICTS_WITH:
            cid = compute_constraint_id(
                "mutual_exclusion",
                fact.subject,
                [fact.fact_id],
            )
            constraints.append(
                MutualExclusionConstraint(
                    constraint_id=cid,
                    target_entity=fact.subject,
                    source_fact_ids=[fact.fact_id],
                    conflicts_with=str(fact.value),
                )
            )

    for subject in sorted(enum_facts_by_subject):
        facts = sorted(
            enum_facts_by_subject[subject],
            key=lambda fact: fact.fact_id,
        )
        fact_ids = [fact.fact_id for fact in facts]
        allowed_values = sorted({str(fact.value) for fact in facts})

        cid = compute_constraint_id(
            "enum",
            subject,
            fact_ids,
        )

        constraints.append(
            EnumConstraint(
                constraint_id=cid,
                target_entity=subject,
                source_fact_ids=fact_ids,
                allowed_values=allowed_values,
            )
        )

    for subject in sorted(range_facts_by_subject):
        facts = sorted(
            range_facts_by_subject[subject],
            key=lambda fact: fact.fact_id,
        )
        min_val: int | float | None = None
        max_val: int | float | None = None
        fact_ids = [fact.fact_id for fact in facts]

        for fact in facts:
            if (
                fact.predicate == SemanticPredicate.HAS_MINIMUM
                and isinstance(fact.value, (int, float))
            ):
                if min_val is not None and min_val != fact.value:
                    raise ValueError(
                        f"Conflicting minimum bounds for {subject}: "
                        f"{min_val} vs {fact.value}"
                    )
                min_val = fact.value

            elif (
                fact.predicate == SemanticPredicate.HAS_MAXIMUM
                and isinstance(fact.value, (int, float))
            ):
                if max_val is not None and max_val != fact.value:
                    raise ValueError(
                        f"Conflicting maximum bounds for {subject}: "
                        f"{max_val} vs {fact.value}"
                    )
                max_val = fact.value

        cid = compute_constraint_id(
            "range",
            subject,
            fact_ids,
        )

        constraints.append(
            RangeConstraint(
                constraint_id=cid,
                target_entity=subject,
                source_fact_ids=fact_ids,
                min_value=min_val,
                max_value=max_val,
            )
        )

    return constraints
