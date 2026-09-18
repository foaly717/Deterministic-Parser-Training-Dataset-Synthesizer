REQUIRED_FIELDS = {
    "instruction",
    "context",
    "response",
}


def validate_candidate_structure(item: dict) -> bool:
    if not isinstance(item, dict):
        return False

    if not REQUIRED_FIELDS.issubset(item):
        return False

    if not isinstance(item["instruction"], str):
        return False

    if not item["instruction"].strip():
        return False

    if not isinstance(item["response"], str):
        return False

    if not item["response"].strip():
        return False

    if item["context"] is not None and not isinstance(item["context"], str):
        return False

    return True
