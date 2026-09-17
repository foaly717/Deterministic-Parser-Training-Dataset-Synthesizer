import hashlib
from pathlib import Path

from dataset_tools.evidence.schema import (
    EvidenceSource,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)
from dataset_tools.parsers.man_page import parse_man_page

from .base import EvidenceLoader


class ManPageLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return ".man." in path.name or path.suffix == ".1"

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        source = EvidenceSource(
            source_id=path.stem,
            path=str(path),
            source_type="man_page",
            sha256=sha256,
        )

        facts = [
            NormalizedEvidenceFact(
                category="man_section",
                subject=entry.tool or path.stem,
                predicate="contains",
                value=entry.name,
                metadata={
                    "section": entry.section,
                    "source_line_start": entry.line_start,
                    "source_line_end": entry.line_end,
                },
            )
            for entry in parse_man_page(path, tool_name=path.stem)
        ]

        return NormalizedEvidenceDocument(
            source=source,
            facts=facts,
        )
