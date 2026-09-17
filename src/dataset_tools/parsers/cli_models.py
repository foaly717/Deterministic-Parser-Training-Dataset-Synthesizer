from dataclasses import dataclass, field


@dataclass
class CLIOption:
    name: str
    aliases: list[str] = field(default_factory=list)
    argument: str | None = None
    description: str | None = None
    section: str | None = None
    source_id: str | None = None
    source_sha256: str | None = None
    parent_command: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    tool: str | None = None
