import hashlib
import re
from pathlib import Path

from dataset_tools.evidence.ids import document_id, fact_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.schema import (
    FactCategory,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
)


def extract_cli_option_facts(
    content: str,
    doc_id: str,
    source_id: str,
    source_sha256: str,
    subject: str = "cli",
) -> list[NormalizedEvidenceFact]:
    """Extract option facts from standard CLI help text without file loading or side effects."""
    facts: list[NormalizedEvidenceFact] = []
    lines = content.splitlines()

    option_pattern = re.compile(
        r"^\s*((?:--?[^\s,]+,?\s*)+)"
        r"(<[^>]+>|\S+)?\s*(.*)$"
    )
    usage_option_pattern = re.compile(r"(?<!\w)--?[A-Za-z0-9][A-Za-z0-9_-]*")

    for idx, line in enumerate(lines, start=1):
        line_str = line.strip()

        if re.match(r"^(usage:|Usage:)", line_str):
            for match in usage_option_pattern.finditer(line_str):
                opt_name = match.group(0)

                provenance = Provenance(
                    source_id=source_id,
                    source_sha256=source_sha256,
                    line_start=idx,
                    line_end=idx,
                    raw_snippet=line,
                )

                facts.append(
                    NormalizedEvidenceFact(
                        fact_id=fact_id(
                            doc_id,
                            FactCategory.CLI_OPTION.value,
                            subject,
                            "supports",
                            opt_name,
                            provenance.model_dump(),
                        ),
                        document_id=doc_id,
                        category=FactCategory.CLI_OPTION,
                        subject=subject,
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
                )

        elif line_str.startswith("-") and not line_str.startswith("---"):
            match = option_pattern.match(line)

            if match:
                raw_option = match.group(1).strip()
                arg_type = match.group(2) or "none"
                desc = match.group(3) or "No description"

                option_names = [
                    option.strip().rstrip(",")
                    for option in raw_option.split(",")
                    if option.strip()
                ]

                for opt_name in option_names:
                    provenance = Provenance(
                        source_id=source_id,
                        source_sha256=source_sha256,
                        line_start=idx,
                        line_end=idx,
                        raw_snippet=line,
                    )

                    fact = NormalizedEvidenceFact(
                        fact_id=fact_id(
                            doc_id,
                            FactCategory.CLI_OPTION.value,
                            subject,
                            "supports",
                            opt_name,
                            provenance.model_dump(),
                        ),
                        document_id=doc_id,
                        category=FactCategory.CLI_OPTION,
                        subject=subject,
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


    return facts


class CLIHelpLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in {".txt", ".help"}:
            return False

        return self._looks_like_cli_help(path)

    def _looks_like_cli_help(self, path: Path) -> bool:
        try:
            content = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            return False

        has_usage = bool(re.search(r"(?im)^usage:\s", content))

        option_lines = [
            line
            for line in content.splitlines()
            if re.search(r"(^|\s)--?[A-Za-z0-9]", line)
        ]

        return has_usage and len(option_lines) >= 1

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        subject = source_id
        if subject.endswith("-help"):
            subject = subject[:-5]
        elif subject.endswith("_help"):
            subject = subject[:-5]

        facts = extract_cli_option_facts(
            content=content,
            doc_id=doc_id,
            source_id=source_id,
            source_sha256=sha256,
            subject=subject,
        )

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="cli_help",
            source_sha256=sha256,
            facts=facts,
        )
