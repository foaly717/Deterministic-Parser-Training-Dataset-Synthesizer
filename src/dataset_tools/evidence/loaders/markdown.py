from pathlib import Path
import hashlib

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)

from .base import EvidenceLoader


class MarkdownEvidenceLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in {".md", ".markdown"}

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        facts = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if not line.strip():
                continue

            provenance = Provenance(
                source_id=source_id,
                source_sha256=sha256,
                line_start=line_number,
                line_end=line_number,
                raw_snippet=line,
            )

            facts.append(
                NormalizedEvidenceFact(
                    fact_id=fact_id(
                        doc_id,
                        "markdown",
                        path.name,
                        "contains",
                        line,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    category="markdown",
                    subject=path.name,
                    predicate="contains",
                    value=line,
                    provenance=provenance,
                )
            )

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="markdown",
            source_sha256=sha256,
            facts=facts,
        )
