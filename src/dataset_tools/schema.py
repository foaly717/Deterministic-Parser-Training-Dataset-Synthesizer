from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EvidenceFact:
    source_id: str
    source_sha256: str
    tool: Optional[str]
    kind: str  # e.g., "option", "subcommand"
    name: str  # e.g., "--main-feature"
    description: Optional[str] = None
    aliases: list[str] = field(default_factory=list)
    argument: Optional[str] = None
    parent_command: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    section: Optional[str] = None


@dataclass
class TrainingExample:
    id: str
    instruction: str
    context: Optional[str]
    response: str
    source_sha256: str
    generator_model: str
    status: str = "candidate"  # "candidate", "accepted", "rejected", "needs_review"
    validation_logs: list[str] = field(default_factory=list)
