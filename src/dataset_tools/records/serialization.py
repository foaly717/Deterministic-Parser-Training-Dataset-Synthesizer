"""Deterministic JSONL serialization for RunRecord."""

import json
from typing import TextIO

from dataset_tools.records.model import RunRecord


def serialize_run_record(record: RunRecord) -> str:
    """Serialize one RunRecord to canonical JSON without a newline."""
    return json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def write_run_record(record: RunRecord, stream: TextIO) -> None:
    """Write exactly one canonical JSONL record."""
    stream.write(serialize_run_record(record))
    stream.write("\n")
