from dataset_tools.evidence.schema import NormalizedEvidenceFact


def select_generation_fact(
    facts: list[NormalizedEvidenceFact],
    index: int,
) -> NormalizedEvidenceFact:
    """Select one deterministic evidence fact for generation."""
    if not facts:
        raise ValueError("At least one evidence fact is required")

    return facts[index % len(facts)]
