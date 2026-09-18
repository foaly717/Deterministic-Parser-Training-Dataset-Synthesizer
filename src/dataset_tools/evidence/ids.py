import hashlib
import json
from typing import Any


def deterministic_id(*parts: Any) -> str:
    """Return a stable SHA-256 identifier for deterministic pipeline artifacts."""
    payload = json.dumps(
        parts,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def document_id(source_id: str, source_sha256: str) -> str:
    return deterministic_id("document", source_id, source_sha256)


def fact_id(
    document_id: str,
    category: str,
    subject: str,
    predicate: str,
    value: Any,
    provenance: dict[str, Any],
) -> str:
    return deterministic_id(
        "fact",
        document_id,
        category,
        subject,
        predicate,
        value,
        provenance,
    )


def constraint_id(
    constraint_type: str,
    target_entity: str,
    source_fact_ids: list[str],
    parameters: dict[str, Any],
) -> str:
    return deterministic_id(
        "constraint",
        constraint_type,
        target_entity,
        sorted(source_fact_ids),
        parameters,
    )
