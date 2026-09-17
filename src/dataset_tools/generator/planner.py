from dataset_tools.schema import EvidenceFact


def select_generation_fact(
    facts: list[EvidenceFact],
    index: int,
) -> EvidenceFact:
    """Select one deterministic evidence fact for generation."""
    if not facts:
        raise ValueError("At least one evidence fact is required")

    return facts[index % len(facts)]
