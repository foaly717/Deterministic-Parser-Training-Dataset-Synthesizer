from collections import defaultdict

from dataset_tools.evidence.schema import (
    EnumConstraint,
    NormalizedEvidenceDocument,
    TypeConstraint,
)
from dataset_tools.evidence.ids import constraint_id


def extract_constraints(
    document: NormalizedEvidenceDocument,
) -> list:
    constraints = []

    enum_facts = defaultdict(list)
    type_facts = []

    for fact in document.facts:
        if (
            fact.category == "enum_value"
            and fact.predicate == "enumerates"
        ):
            enum_facts[fact.subject].append(fact)

        elif (
            fact.category == "cli_option"
            and fact.predicate == "accepts_type"
        ):
            type_facts.append(fact)

    for target_entity, facts in enum_facts.items():
        source_fact_ids = sorted(
            fact.fact_id for fact in facts
        )

        allowed_values = sorted(
            {
                str(fact.value)
                for fact in facts
            }
        )

        constraints.append(
            EnumConstraint(
                constraint_id=constraint_id(
                    "enum",
                    target_entity,
                    source_fact_ids,
                    {
                        "allowed_values": allowed_values,
                    },
                ),
                target_entity=target_entity,
                source_fact_ids=source_fact_ids,
                allowed_values=allowed_values,
            )
        )

    for fact in type_facts:
        constraints.append(
            TypeConstraint(
                constraint_id=constraint_id(
                    "type",
                    fact.subject,
                    [fact.fact_id],
                    {
                        "expected_type": str(fact.value),
                    },
                ),
                target_entity=fact.subject,
                source_fact_ids=[fact.fact_id],
                expected_type=(
                    "str"
                    if fact.value == "string"
                    else str(fact.value)
                ),
            )
        )

    return constraints
