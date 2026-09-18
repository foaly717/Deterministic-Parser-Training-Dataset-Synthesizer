import hashlib
import re
from pathlib import Path

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.schema import (
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)

from .base import EvidenceLoader


class FFmpegLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return "ffmpeg" in path.name.lower()

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8", errors="replace")

        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        facts: list[NormalizedEvidenceFact] = []
        lines = content.splitlines()

        option_pattern = re.compile(r"^\s*(-\S+)\s+(<[^>]+>|\S+)?\s*(.*)$")
        usage_option_pattern = re.compile(
            r"(?<!\S)--?[A-Za-z0-9][A-Za-z0-9_-]*"
        )

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()

            if re.match(r"^(usage:|Usage:)", line_str):
                for match in usage_option_pattern.finditer(line_str):
                    opt_name = match.group(0)

                    provenance = Provenance(
                        source_id=source_id,
                        source_sha256=sha256,
                        line_start=idx,
                        line_end=idx,
                        raw_snippet=line,
                    )
                    fact = NormalizedEvidenceFact(
                        fact_id=fact_id(
                            doc_id,
                            "cli_option",
                            "ffmpeg",
                            "supports",
                            opt_name,
                            provenance.model_dump(),
                        ),
                        document_id=doc_id,
                        category="cli_option",
                        subject="ffmpeg",
                        predicate="supports",
                        value=opt_name,
                        provenance=provenance,
                        metadata={
                            "kind": "option",
                            "aliases": [],
                            "argument": "none",
                            "description": "Referenced in usage syntax",
                        },
                    )
                    facts.append(fact)

            elif line_str.startswith("-") and not line_str.startswith("---"):
                match = option_pattern.match(line)
                if match:
                    opt_name = match.group(1).strip()
                    arg_type = match.group(2) or "none"
                    desc = match.group(3) or "No description"

                    provenance = Provenance(
                        source_id=source_id,
                        source_sha256=sha256,
                        line_start=idx,
                        line_end=idx,
                        raw_snippet=line,
                    )
                    fact = NormalizedEvidenceFact(
                        fact_id=fact_id(
                            doc_id,
                            "cli_option",
                            "ffmpeg",
                            "supports",
                            opt_name,
                            provenance.model_dump(),
                        ),
                        document_id=doc_id,
                        category="cli_option",
                        subject="ffmpeg",
                        predicate="supports",
                        value=opt_name,
                        provenance=provenance,
                        metadata={
                            "kind": "option",
                            "aliases": [],
                            "argument": arg_type.strip(),
                            "description": desc.strip(),
                        },
                    )
                    facts.append(fact)

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="ffmpeg",
            source_sha256=sha256,
            facts=facts,
        )
