from pathlib import Path
import hashlib

from dataset_tools.evidence.schema import (
    EvidenceSource,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)

from dataset_tools.parsers.cli_help import parse_cli_help

from .base import EvidenceLoader


class HandBrakeCliLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return path.name == "handbrakecli-help.txt"

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")

        sha256 = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        source = EvidenceSource(
            source_id=path.stem,
            path=str(path),
            source_type="handbrakecli",
            sha256=sha256,
        )

        facts = [
            NormalizedEvidenceFact(
                category="cli_option",
                subject=fact.tool or "HandBrakeCLI",
                predicate="supports",
                value=fact.name,
                metadata={
                    "kind": fact.kind,
                    "aliases": fact.aliases,
                    "argument": fact.argument,
                    "description": fact.description,
                    "source_id": fact.source_id,
                    "source_line_start": fact.line_start,
                    "source_line_end": fact.line_end,
                },
            )
            for fact in parse_cli_help(path)
            if fact.kind == "option"
        ]

        return NormalizedEvidenceDocument(
            source=source,
            facts=facts,
        )
