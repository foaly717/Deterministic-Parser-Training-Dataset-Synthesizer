import hashlib
import json

def deterministic_id(
    prefix: str,
    *args: list | dict | str | int | float | bool | None,
) -> str:
    serialized = json.dumps(args, separators=(",", ":"), ensure_ascii=True, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"

def compute_document_id(source_id: str, source_sha256: str) -> str:
    return deterministic_id("document", source_id, source_sha256)

def compute_fact_id(
    document_id: str,
    subject: str,
    predicate: str,
    value: str | int | float | bool | None,
    provenance: dict | str = "",
) -> str:
    return deterministic_id(
        "fact",
        document_id,
        subject,
        predicate,
        value,
        provenance,
    )

def compute_constraint_id(constraint_type: str, target_entity: str, source_fact_ids: list[str]) -> str:
    sorted_facts = sorted(source_fact_ids)
    return deterministic_id("constraint", constraint_type, target_entity, sorted_facts)
