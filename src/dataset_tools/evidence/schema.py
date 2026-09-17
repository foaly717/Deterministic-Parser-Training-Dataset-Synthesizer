from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceSource:
    source_id: str
    path: str
    source_type: str
    sha256: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedEvidenceFact:
    category: str
    subject: str
    predicate: str
    value: str
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_type: str | None = None


@dataclass
class NormalizedEvidenceDocument:
    source: EvidenceSource
    facts: list[NormalizedEvidenceFact]
    constraints: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": {
                "source_id": self.source.source_id,
                "path": self.source.path,
                "source_type": self.source.source_type,
                "sha256": self.source.sha256,
                "metadata": self.source.metadata,
            },
            "constraints": [
                {
                    "name": constraint.name,
                    "category": constraint.category,
                    "subject": constraint.subject,
                    "metadata": constraint.metadata,
                    "allowed_values": getattr(
                        constraint,
                        "allowed_values",
                        None,
                    ),
                }
                for constraint in self.constraints
            ],
            "facts": [
                {
                    "category": fact.category,
                    "subject": fact.subject,
                    "predicate": fact.predicate,
                    "value": fact.value,
                    "metadata": fact.metadata,
                }
                for fact in self.facts
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NormalizedEvidenceDocument":
        source_data = data["source"]
        return cls(
            source=EvidenceSource(
                source_id=source_data["source_id"],
                path=source_data["path"],
                source_type=source_data["source_type"],
                sha256=source_data["sha256"],
                metadata=source_data.get("metadata", {}),
            ),
            facts=[
                NormalizedEvidenceFact(
                    category=item["category"],
                    subject=item["subject"],
                    predicate=item["predicate"],
                    value=item["value"],
                    metadata=item.get("metadata", {}),
                )
                for item in data.get("facts", [])
            ],
        )
