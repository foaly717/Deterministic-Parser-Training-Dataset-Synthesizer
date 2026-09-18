import hashlib
import re
from pathlib import Path

from dataset_tools.evidence.schema import (
    EvidenceSource,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
)

from .base import EvidenceLoader


class FFmpegLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return "ffmpeg" in path.name.lower()

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8", errors="replace")

        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        source = EvidenceSource(
            source_id=path.stem,
            path=str(path),
            source_type="ffmpeg",
            sha256=sha256,
        )

        facts: list[NormalizedEvidenceFact] = []
        lines = content.splitlines()

        option_pattern = re.compile(r"^\s*(-\S+)\s+(<[^>]+>|\S+)?\s*(.*)$")

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if line_str.startswith("-") and not line_str.startswith("---"):
                match = option_pattern.match(line)
                if match:
                    opt_name = match.group(1).strip()
                    arg_type = match.group(2) or "none"
                    desc = match.group(3) or "No description"

                    fact = NormalizedEvidenceFact(
                        category="cli_option",
                        subject="ffmpeg",
                        predicate="supports",
                        value=opt_name,
                        metadata={
                            "kind": "option",
                            "aliases": [],
                            "argument": arg_type.strip(),
                            "description": desc.strip(),
                            "source_id": path.stem,
                            "source_line_start": idx,
                            "source_line_end": idx,
                        },
                    )
                    facts.append(fact)

        return NormalizedEvidenceDocument(
            source=source,
            facts=facts,
        )
