from dataset_tools.generator.runner import validate_candidate_structure


def test_candidate_structure_accepts_single_object():
    assert validate_candidate_structure({
        "instruction": "Do something",
        "context": "evidence",
        "response": "HandBrakeCLI --preset-export Test",
    }) is True


def test_candidate_structure_rejects_array_as_candidate():
    assert validate_candidate_structure([
        {
            "instruction": "Do something",
            "context": "evidence",
            "response": "HandBrakeCLI --preset-export Test",
        }
    ]) is False
