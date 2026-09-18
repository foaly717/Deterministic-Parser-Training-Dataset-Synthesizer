from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FactCategory(str, Enum):
    CLI_OPTION = "cli_option"
    CLI_CONSTRAINT = "cli_constraint"
    ENUM_VALUE = "enum_value"
    DOCUMENT_SECTION = "document_section"
    MARKDOWN_STRUCT = "markdown_struct"

    # Existing loader categories retained during migration.
    TEXT = "text"
    MARKDOWN = "markdown"
    MAN_SECTION = "man_section"


class ConstraintType(str, Enum):
    TYPE = "type"
    ENUM = "enum"
    RANGE = "range"
    DEPENDENCY = "dependency"
    MUTUAL_EXCLUSION = "mutual_exclusion"


class Provenance(BaseModel):
    """Exact source location and artifact identity for a normalized fact."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_sha256: str
    line_start: int | None = None
    line_end: int | None = None
    section: str | None = None
    raw_snippet: str | None = None


class NormalizedEvidenceFact(BaseModel):
    """Atomic declarative observation extracted from evidence."""

    model_config = ConfigDict(extra="forbid")

    fact_id: str
    document_id: str
    category: FactCategory
    subject: str
    predicate: str
    value: str | int | float | bool | None
    provenance: Provenance
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedEvidenceDocument(BaseModel):
    """Deterministic normalized container for one source artifact's facts."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    source_id: str
    source_type: str
    source_sha256: str
    facts: list[NormalizedEvidenceFact] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DerivedConstraintBase(BaseModel):
    """Base operational rule derived strictly from evidence facts."""

    model_config = ConfigDict(extra="forbid")

    constraint_id: str
    target_entity: str
    source_fact_ids: list[str] = Field(default_factory=list)


class TypeConstraint(DerivedConstraintBase):
    """Unbounded typed constraint when evidence does not enumerate values."""

    constraint_type: Literal["type"] = "type"
    expected_type: str


class EnumConstraint(DerivedConstraintBase):
    """Discrete enumeration constraint requiring explicit values."""

    constraint_type: Literal["enum"] = "enum"
    allowed_values: list[str] = Field(min_length=1)


class RangeConstraint(DerivedConstraintBase):
    """Numeric range constraint with validated bounds."""

    constraint_type: Literal["range"] = "range"
    min_value: int | float | None = None
    max_value: int | float | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> "RangeConstraint":
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            raise ValueError("min_value must not exceed max_value")
        return self


class DependencyConstraint(DerivedConstraintBase):
    """Prerequisite constraint requiring another flag or option."""

    constraint_type: Literal["dependency"] = "dependency"
    requires_flag: str


class MutualExclusionConstraint(DerivedConstraintBase):
    """Constraint preventing flags from being used concurrently."""

    constraint_type: Literal["mutual_exclusion"] = "mutual_exclusion"
    conflicts_with: list[str] = Field(min_length=1)


DerivedConstraint = Annotated[
    TypeConstraint
    | EnumConstraint
    | RangeConstraint
    | DependencyConstraint
    | MutualExclusionConstraint,
    Field(discriminator="constraint_type"),
]
