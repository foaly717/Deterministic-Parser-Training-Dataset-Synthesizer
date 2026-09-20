"""Canonical run-record models, construction, and serialization."""

from dataset_tools.records.builder import build_run_record
from dataset_tools.records.model import (
    CandidateModel,
    RunRecord,
    ValidationBlock,
    ValidationStage,
    example_id,
    normalize_text,
)
from dataset_tools.records.serialization import (
    serialize_run_record,
    write_run_record,
)

__all__ = [
    "CandidateModel",
    "RunRecord",
    "ValidationBlock",
    "ValidationStage",
    "example_id",
    "normalize_text",
    "build_run_record",
    "serialize_run_record",
    "write_run_record",
]
