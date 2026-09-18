from dataclasses import dataclass, field


@dataclass
class EvidenceIndex:
    valid_options: set[str] = field(default_factory=set)
    constraints: dict[str, set[str]] = field(default_factory=dict)


def build_evidence_index(document):
    valid_options: set[str] = set()
    constraints: dict[str, set[str]] = {}

    for fact in document.facts:
        if fact.category == "cli_option" and fact.predicate == "supports":
            valid_options.add(fact.value)

        elif fact.category == "cli_constraint" and fact.extraction_type == "enum":
            allowed_values = fact.metadata.get("allowed_values")
            if allowed_values:
                constraints.setdefault(fact.subject, set()).update(allowed_values)

    for constraint in getattr(document, "constraints", []):
        subject = getattr(constraint, "subject", None)
        allowed_values = getattr(constraint, "allowed_values", None)

        if subject and allowed_values:
            constraints.setdefault(subject, set()).update(allowed_values)

    return EvidenceIndex(
        valid_options=valid_options,
        constraints=constraints,
    )
