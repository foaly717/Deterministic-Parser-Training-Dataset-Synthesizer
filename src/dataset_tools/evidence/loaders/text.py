from pathlib import Path
import hashlib

from dataset_tools.evidence.schema import (
    EvidenceSource,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)

from .base import EvidenceLoader


class TextEvidenceLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return path.suffix in {".txt", ".md"}

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")

        sha256 = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        source = EvidenceSource(
            source_id=path.stem,
            path=str(path),
            source_type="text",
            sha256=sha256,
        )

        facts = [
            NormalizedEvidenceFact(
                category="text",
                subject=path.name,
                predicate="contains",
                value=line,
            )
            for line in content.splitlines()
            if line.strip()
        ]

        return NormalizedEvidenceDocument(
            source=source,
            facts=facts,
        )
