from pathlib import Path
import hashlib

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)

from dataset_tools.parsers.cli_help import parse_cli_help


def extract_enum_values(description: str | None) -> list[str]:
    if not description:
        return []

    values = []
    collecting = False

    for line in description.splitlines():
        value = line.strip()

        if value.endswith(":"):
            collecting = True
            continue

        if collecting:
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

from .base import EvidenceLoader


class HandBrakeCliLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return path.name == "handbrakecli-help.txt"

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        facts = []
        for parsed_fact in parse_cli_help(path):
            provenance = Provenance(
                source_id=source_id,
                source_sha256=sha256,
                line_start=parsed_fact.line_start,
                line_end=parsed_fact.line_end,
                section=parsed_fact.section,
            )


            enum_values = extract_enum_values(
                parsed_fact.description
            )

            for enum_value in enum_values:
                enum_provenance = Provenance(
                    source_id=source_id,
                    source_sha256=sha256,
                    line_start=parsed_fact.line_start,
                    line_end=parsed_fact.line_end,
                    section=parsed_fact.section,
                )

                facts.append(
                    NormalizedEvidenceFact(
                        fact_id=fact_id(
                            doc_id,
                            "enum_value",
                            parsed_fact.name,
                            "enumerates",
                            enum_value,
                            enum_provenance.model_dump(),
                        ),
                        document_id=doc_id,
                        category="enum_value",
                        subject=parsed_fact.name,
                        predicate="enumerates",
                        value=enum_value,
                        provenance=enum_provenance,
                    )
                )

            facts.append(
                NormalizedEvidenceFact(
                    fact_id=fact_id(
                        doc_id,
                        "cli_option",
                        parsed_fact.tool or "HandBrakeCLI",
                        "supports",
                        parsed_fact.name,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    category="cli_option",
                    subject=parsed_fact.tool or "HandBrakeCLI",
                    predicate="supports",
                    value=parsed_fact.name,
                    provenance=provenance,
                    metadata={
                        "kind": "option",
                        "aliases": parsed_fact.aliases,
                        "argument": parsed_fact.argument,
                        "description": parsed_fact.description,
                    },
                )
            )

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="handbrakecli",
            source_sha256=sha256,
            facts=facts,
        )
