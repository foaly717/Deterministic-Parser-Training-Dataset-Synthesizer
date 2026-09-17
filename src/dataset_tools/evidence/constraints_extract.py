from dataset_tools.evidence.constraints import EnumConstraint


def extract_enum_constraints(facts):
    constraints = []

    for fact in facts:
        values = fact.metadata.get("allowed_values")

        if values:
            constraints.append(
                EnumConstraint(
                    name=f"{fact.subject}-enum",
                    category="enum",
                    subject=fact.subject,
                    allowed_values=values,
                    metadata={
                        "source_fact": fact.value,
                    },
                )
            )

    return constraints
