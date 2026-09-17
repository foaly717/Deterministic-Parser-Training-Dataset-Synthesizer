from dataclasses import dataclass


@dataclass
class ManEntry:
    name: str
    section: str | None = None
    description: str | None = None
    source_id: str | None = None
    source_sha256: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    tool: str | None = None
