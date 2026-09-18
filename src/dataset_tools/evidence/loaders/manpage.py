import hashlib
from pathlib import Path

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)
from dataset_tools.parsers.man_page import parse_man_page

from .base import EvidenceLoader


class ManPageLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return ".man." in path.name or path.suffix == ".1"

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        facts = []
        for entry in parse_man_page(path, tool_name=path.stem):
            provenance = Provenance(
                source_id=source_id,
                source_sha256=sha256,
                line_start=entry.line_start,
                line_end=entry.line_end,
                section=entry.section,
            )

            facts.append(
                NormalizedEvidenceFact(
                    fact_id=fact_id(
                        doc_id,
                        "man_section",
                        entry.tool or path.stem,
                        "contains",
                        entry.name,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    category="man_section",
                    subject=entry.tool or path.stem,
                    predicate="contains",
                    value=entry.name,
                    provenance=provenance,
                )
            )

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="man_page",
            source_sha256=sha256,
            facts=facts,
        )
