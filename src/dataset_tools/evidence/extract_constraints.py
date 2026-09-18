from dataset_tools.evidence.constraints import EnumConstraint
from dataset_tools.evidence.schema import NormalizedEvidenceDocument


def extract_constraints(
    document: NormalizedEvidenceDocument,
) -> list[EnumConstraint]:
    constraints: list[EnumConstraint] = []

    for fact in document.facts:
        if fact.extraction_type != "enum":
            continue

        constraints.append(
            EnumConstraint(
                name=fact.subject,
                category=fact.category,
                subject=fact.metadata.get("applies_to", fact.subject),
                allowed_values=list(fact.metadata["allowed_values"]),
                metadata={
                    "source_id": document.source.source_id,
                    **fact.metadata,
                },
            )
        )

    return constraints
