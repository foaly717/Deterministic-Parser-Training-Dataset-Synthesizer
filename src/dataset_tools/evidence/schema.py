from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DocumentFormat(str, Enum):
    CLI_HELP = "cli_help"
    MAN_PAGE = "man_page"
    MARKDOWN = "markdown"
    STRUCTURED_JSON = "structured_json"


class SemanticPredicate(str, Enum):
    SUPPORTS = "supports"
    ENUMERATES = "enumerates"
    ACCEPTS_TYPE = "accepts_type"
    HAS_MINIMUM = "has_minimum"
    HAS_MAXIMUM = "has_maximum"
    REQUIRES = "requires"
    CONFLICTS_WITH = "conflicts_with"


class ToolIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str | None = None


class ArtifactIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_sha256: str
    path_or_uri: str | None = None


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: DocumentFormat
    tool: ToolIdentity | None = None
    role: str | None = None


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    line_start: int | None = None
    line_end: int | None = None
    section: str | None = None
    raw_snippet: str | None = None


class NormalizedEvidenceFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str
    document_id: str
    subject: str
    predicate: SemanticPredicate
    value: str | int | float | bool | None
    provenance: Provenance = Field(default_factory=Provenance)


class NormalizedEvidenceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    artifact: ArtifactIdentity
    metadata: DocumentMetadata
    facts: list[NormalizedEvidenceFact] = Field(default_factory=list)


class BaseConstraint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    constraint_id: str
    target_entity: str
    source_fact_ids: list[str]


class TypeConstraint(BaseConstraint):
    constraint_type: Literal["type"] = "type"
    expected_type: str


class EnumConstraint(BaseConstraint):
    constraint_type: Literal["enum"] = "enum"
    allowed_values: list[str] = Field(min_length=1)


class RangeConstraint(BaseConstraint):
    constraint_type: Literal["range"] = "range"
    min_value: int | float | None = None
    max_value: int | float | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> "RangeConstraint":
        if self.min_value is None and self.max_value is None:
            raise ValueError("RangeConstraint requires at least one bound.")

        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            raise ValueError("min_value must not exceed max_value.")

        return self


class DependencyConstraint(BaseConstraint):
    constraint_type: Literal["dependency"] = "dependency"
    requires: str


class MutualExclusionConstraint(BaseConstraint):
    constraint_type: Literal["mutual_exclusion"] = "mutual_exclusion"
    conflicts_with: str


DerivedConstraint = Annotated[
    TypeConstraint
    | EnumConstraint
    | RangeConstraint
    | DependencyConstraint
    | MutualExclusionConstraint,
    Field(discriminator="constraint_type"),
]
