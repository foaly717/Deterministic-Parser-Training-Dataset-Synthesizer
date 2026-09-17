from dataset_tools.evidence.constraints import EnumConstraint
from dataset_tools.evidence.schema import NormalizedEvidenceDocument


def extract_constraints(
    document: NormalizedEvidenceDocument,
) -> list[EnumConstraint]:
    constraints = []

    for fact in document.facts:
        if fact.extraction_type != "enum":
            continue

        constraints.append(
            EnumConstraint(
                name=fact.subject,
                category=fact.category,
                subject=fact.subject,
                allowed_values=fact.metadata["allowed_values"],
                metadata={
                    "source_id": document.source.source_id,
                },
            )
        )

    return constraints
