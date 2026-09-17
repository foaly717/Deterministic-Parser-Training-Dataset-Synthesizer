from dataclasses import dataclass, field
from typing import Any


@dataclass
class Constraint:
    name: str
    category: str
    subject: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnumConstraint(Constraint):
    allowed_values: list[str] = field(default_factory=list)
