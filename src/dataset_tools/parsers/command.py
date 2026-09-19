from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedOption:
    """Normalized CLI option representation."""

    name: str
    value: str | None = None


@dataclass(frozen=True)
class ParsedCommand:
    """Normalized command representation consumed by validators."""

    executable: str
    options: tuple[ParsedOption, ...]
