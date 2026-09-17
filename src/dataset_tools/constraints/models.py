from dataclasses import dataclass


@dataclass(frozen=True)
class EnumConstraint:
    option: str
    values: list[str]
    source_id: str
    source_sha256: str
