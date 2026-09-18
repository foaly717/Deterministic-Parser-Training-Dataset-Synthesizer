from typing import Any


def serialize_validation_result(
    result,
    *,
    candidate: dict | None = None,
    provenance: dict | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    record = {
        "status": result.status,
        "stage": result.stage,
        "reason_code": result.reason_code,
        "validation_logs": result.validation_logs,
    }

    if candidate is not None:
        record["candidate"] = candidate

    if provenance:
        record.update(provenance)

    if extra:
        record.update(extra)

    return record


def serialize_validation_failure(
    *,
    stage: str,
    reason_code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "status": "rejected",
        "stage": stage,
        "reason_code": reason_code,
        "validation_logs": [message],
    }

