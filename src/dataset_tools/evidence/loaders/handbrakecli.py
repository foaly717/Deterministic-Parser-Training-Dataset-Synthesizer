import hashlib
from pathlib import Path

from dataset_tools.evidence.ids import compute_document_id, compute_fact_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
    SemanticPredicate,
    ToolIdentity,
)
from dataset_tools.parsers.cli_help import parse_cli_help


def extract_enum_values(description: str | None) -> list[str]:
    if not description:
        return []

    values: list[str] = []
    collecting = False

    for line in description.splitlines():
        value = line.strip()

        if value.endswith(":"):
            collecting = True
            continue

        if not collecting:
            continue

        if not value:
            continue

        if (
            " " not in value
            and ":" not in value
            and "=" not in value
            and len(value) < 40
        ):
            values.append(value)
        else:
            collecting = False

    return values


class HandBrakeCliLoader(EvidenceLoader):
    def supports(self, path: Path) -> bool:
        return path.name == "handbrakecli-help.txt"

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
        source_id = path.stem
        source_sha256 = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()
        document_id = compute_document_id(
            source_id,
            source_sha256,
        )

        facts: list[NormalizedEvidenceFact] = []

        for parsed in parse_cli_help(path):
            provenance = Provenance(
                line_start=parsed.line_start,
                line_end=parsed.line_end,
                section=parsed.section,
            )

            tool = parsed.tool or "HandBrakeCLI"

            facts.append(
                NormalizedEvidenceFact(
                    fact_id=compute_fact_id(
                        document_id,
                        tool,
                        SemanticPredicate.SUPPORTS.value,
                        parsed.name,
                        provenance.model_dump(),
                    ),
                    document_id=document_id,
                    subject=tool,
                    predicate=SemanticPredicate.SUPPORTS,
                    value=parsed.name,
                    provenance=provenance,
                )
            )

            for enum_value in extract_enum_values(
                parsed.description
            ):
                facts.append(
                    NormalizedEvidenceFact(
                        fact_id=compute_fact_id(
                            document_id,
                            parsed.name,
                            SemanticPredicate.ENUMERATES.value,
                            enum_value,
                            provenance.model_dump(),
                        ),
                        document_id=document_id,
                        subject=parsed.name,
                        predicate=SemanticPredicate.ENUMERATES,
                        value=enum_value,
                        provenance=provenance,
                    )
                )

        return NormalizedEvidenceDocument(
            document_id=document_id,
            artifact=ArtifactIdentity(
                source_id=source_id,
                source_sha256=source_sha256,
                path_or_uri=str(path),
            ),
            metadata=DocumentMetadata(
                format=DocumentFormat.CLI_HELP,
                tool=ToolIdentity(name="HandBrakeCLI"),
            ),
            facts=facts,
        )
