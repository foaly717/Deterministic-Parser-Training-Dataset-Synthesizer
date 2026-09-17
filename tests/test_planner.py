from dataset_tools.generator.planner import select_generation_fact
from dataset_tools.schema import EvidenceFact


def make_fact(name):
    return EvidenceFact(
        source_id="test",
        source_sha256="abc",
        tool="HandBrakeCLI",
        kind="option",
        name=name,
    )


def test_select_generation_fact_is_deterministic():
    facts = [make_fact("--one"), make_fact("--two")]

    assert select_generation_fact(facts, 0).name == "--one"
    assert select_generation_fact(facts, 1).name == "--two"
    assert select_generation_fact(facts, 2).name == "--one"
